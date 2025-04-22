import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")
sys.path.insert(3, "../routers")

from states.agent_state import AIState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.load import load, dumpd
from langgraph.prebuilt import ToolNode

from datetime import datetime
import re
import json
import logging
from typing import Optional, Dict, List, Mapping, Tuple, Union, Any, Callable, Awaitable
import uuid

from constants.credentials import OPENAI_API_KEY

from routers.whoop_connect import (
    get_valid_whoop_token,
)
from dependencies.whoop_dependencies import (
    get_whoop_body_measurements,
    get_whoop_cycle,
    get_whoop_sleep,
    get_whoop_user
)

from dependencies.firebase_dependencies import (
    get_profile, get_survey_context
)
from dependencies.rag_dependencies import query_docs_from_chroma

WHOOP_UTILS_MAPPER = {
    "data.whoop.cycle": get_whoop_cycle,
    "data.whoop.sleep": get_whoop_sleep,
    "data.whoop.user": get_whoop_user,
    "data.whoop.body_measurements": get_whoop_body_measurements
}

def get_llm():
    """Return the LLM."""
    try:
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=OPENAI_API_KEY,
            max_retries=3,
        )
    except Exception as e:
        print(f"❌ Error initializing LLM: {str(e)}")
        raise

class Agent:
    
    def __init__(self, user_id: str, thread_id: Optional[str] = None, config: Optional[dict] = None):
        ## ----- ID -----
        self.thread_id: str = thread_id or str(uuid.uuid4())
        self.user_id: str = user_id

        ## ----- LOG PREPARATION -----
        self.logger: logging.Logger = self.initialize_logger()

        ## ----- GRAPH SETUP -----
        self.state: AIState = self._initialize_state()
        self.config: Dict = config or {}
        self.graph = self.build_graph()

        ## ----- GRAPH TOOL -----
        self.tools = {
            "data.whoop": self.fetch_whoop,
            "data.vector": self.fetch_vector,
            "knowledge.tavily": self.search_tavily
        }
        self.datatypes = {
            "whoop": [
                ("cycle", 
                    "Represents a user’s full-day physiological summary from sleep to sleep. " +
                    "Includes strain (cardiovascular load), energy burned, average and max heart rate. " + 
                    "Useful for understanding daily exertion, recovery, and heart activity patterns. "
                ), 
                ("body_measurements", 
                    "Contains the user’s physical metrics: height (in meters), weight (in kilograms), and maximum heart rate. " + 
                    "Essential for tailoring health recommendations and analyzing fitness levels."
                ),
                ("user",
                    "Provides basic user profile information, including first and last name, email address, and WHOOP user ID. " +
                    "Useful for personalizing interactions and managing user accounts." 
                ),
                ("sleep", 
                    "Details each sleep session, including start and end times, duration, and classification as a nap or main sleep. " +
                    "When scored, it provides insights into sleep stages (light, deep, REM), total time in bed, and periods awake. " +
                    "Valuable for assessing sleep quality and recovery." 
                )
            ],
        }

        ## ----- GRAPH SYSTEM SETUP -----        
        self.system_prompt = SystemMessage(
            content=(
                "You are a health assistant providing educational, general information about health. "
                "You explain medical concepts, describe common symptoms and conditions, and offer generic advice. "
                "You do NOT provide personalized diagnoses or definitive medical opinions. "
                "Avoid phrasing like 'you have X'; instead use general phrasing such as "
                "'the symptoms you mention are common in X'.\n\n"
                # "User Profile:\n" ## TODO: Unlabel when integrating with server
                # f"{get_survey_context(survey_data=get_profile(user_id=self.user_id))}"
            )
        )

        ## ----- LLM Setup -----
        ## technically both share the same system prompt, refer to _initialize_state
        self.llm_with_tools = get_llm().bind_tools(self.tools.values(), parallel_tool_calls=True)
        self.llm_pure = get_llm()

    def initialize_logger(self) -> logging.Logger: 
        """Initialize Logger Object"""

        _logger = logging.getLogger(f"Agent.{self.user_id}.{self.thread_id}")
        _logger.setLevel(logging.DEBUG)
        if not self.logger.handlers:
            # Stream (console) handler
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter(
                f"[%(asctime)s] [%(levelname)s] [{self.user_id}:{self.thread_id}] %(message)s"
            ))
            _logger.addHandler(stream_handler)
        return _logger
    
    def get_data_tool_identifiers_with_description(self) -> List[Tuple[str, str]]:
        """Preprocess List[str] with datatype identifiers `data.<provider>.<datatype>`
        
        Returns:
            List[Tuple[str, str]]: [("data.whoop.sleep", "Explain this this this..."), ...]
        """
        
        provider_datatype = []
        for provider, types in self.datatypes.items():
            provider_datatype += [(f"data.{provider}.{_type[0]}", _type[1]) for _type in types] 
        return provider_datatype

    def get_knowledge_tool_identifiers(self) -> List[str]:
        """Preprocess List[str] with knowledge tools
        
        Returns:
            List[str]: ["knowledge.tavily", ...]
        """

        knowledge_tools = [knowledge_tool for knowledge_tool in self.tools if knowledge_tool.split(".")[0] == "knowledge"]
        return knowledge_tools

    def new_prompt_clear(self):
        """Clear message specific, non-reuseable state variables"""
        
        self.state["data_mining_cycle"] = 0
        self.state["knowledge_mining_cycle"] = 0
        self.state["message_tool_messages"].clear()
        self.state["tmp_data"].clear()
        self.state["tmp_issues"].clear()
        self.state["message_data"].clear()
        self.state["message_knowledge"].clear()
        self.state["tmp_knowledge"].clear()
        self.state["active_flow_label"].clear()
        self.state["final_response"] = {}
        self.state["response_scores"] = {}
        self.state["message_data_dimensions"] = {}
        self.state["tmp_data_dimensions"] = {}

    def _initialize_state(self) -> AIState:
        ## can take a User object in here as well, so do the firestore data retrieval in init() 
        ## then feed it into this function for initializing basic_user_profile

        ### Resposne Pathways 
        ###
        ### 1. Casual or Non-health --> Kindly guide user back to health discussion
        ### 2. Hella-Vague Message --> Empathize & guide user back to health discussion
        ### 3.1. Data Extraction Needed, Response should consist of:
        ###          - datatype needed w/ explanation ==> `data.whoop.sleep`: `This can uncover user's sleep pattern, which is related to <condition>.`, etc.
        ### 3.2. Knowledge Mining Needed, Response should consist of:
        ###          - knowledge provider w/ explanation ==> `knowledge.tavily`: `Generic search tool allows us to find overall information.`, etc.
        ### 3.3. Compile Response, Response is a general AIMessage()
        ### 3.4. Compile Clarification Question, Response is a general AIMessage()
        ###          - question needs to be explained however, so AIMessage.content should have:
        ###                     - Question
        ###                     - Why the question is needed / What is the connection

        ## retrieve user data from firestore using user_id
        
        _state = AIState(
            thread_id=self.thread_id,
            user_id=self.user_id,
            session_last_updatedAt=datetime.now(), 
            conversation_history=[],
            last_user_message=None,
            last_ai_message=None,
            message_tool_messages=[],
            message_role_scores=None,
                    # {
                    #     "query": 0.0, 
                    #     "context": 0.0,
                    #     "casual": 0.0,
                    #     "non-health": 0.0,
                    #     "vague": 0.0
                    # }
            dominant_role=None,
            intent_scores=None,
                    # {
                    #     "personal": None,
                    #     "general": None,
                    #     "hypothetical": None,
                    #     "generic": None
                    # }
            dominant_intent=None,
            message_features=None,
            clarification_prompt=None,
                    # [{
                    #     "clarification_question": "Could you tell me how long you've been experiencing this fatigue?",
                    #     "clarification_reason": "This information will help determine whether the issue is acute, like a short-term illness, or chronic, which may suggest something more systemic.",
                    #     "is_clarification_turn": true
                    # }, ...]
            is_clarification_turn=None,
            clarification_depth=None,
            active_flow_label=[],
            issues=[],
            tmp_issues=[],
            message_data=[],
            data=[],
            tmp_data=[],
            tmp_data_dimensions={},
            message_data_dimensions={},
            target_data_dimensions={},
            message_knowledge=[],
            knowledge=[],
            tmp_knowledge=[],
            data_mining_cycle=0,
            knowledge_mining_cycle=0,
            final_response=None,
            response_scores=None
        )
        
        _state["conversation_history"].append(self.system_prompt)

        return _state

    def export_state_as_dict(self) -> Dict:
        """Export state of agent as a Dict obj"""

        _state: Dict[str, Any] = {}

        # Serialize conversation history and messages
        _state["conversation_history"] = [dumpd(msg) for msg in self.state["conversation_history"]]
        _state["last_ai_message"] = dumpd(self.state["last_ai_message"]) if self.state["last_ai_message"] else None
        _state["last_user_message"] = dumpd(self.state["last_user_message"]) if self.state["last_user_message"] else None
        _state["message_tool_messages"] = [dumpd(msg) for msg in self.state["message_tool_messages"]]
        
        # Primitive fields
        _state["thread_id"] = self.state["thread_id"]
        _state["user_id"] = self.state["user_id"]
        _state["session_last_updatedAt"] = self.state["session_last_updatedAt"]

        # Scores and roles
        _state["message_role_scores"] = self.state["message_role_scores"]
        _state["dominant_role"] = self.state["dominant_role"]
        _state["intent_scores"] = self.state["intent_scores"]
        _state["dominant_intent"] = self.state["dominant_intent"]
        _state["message_features"] = self.state["message_features"]
        
        # Clarification fields
        _state["clarification_prompt"] = self.state["clarification_prompt"]
        _state["is_clarification_turn"] = self.state["is_clarification_turn"]
        _state["clarification_depth"] = self.state["clarification_depth"]
        
        
        # Flow labels and issues
        _state["active_flow_label"] = list(self.state["active_flow_label"])
        _state["issues"] = list(self.state["issues"])
        _state["tmp_issues"] = list(self.state["tmp_issues"])

        # Data dimensions and payloads
        _state["target_data_dimensions"] = self.state["target_data_dimensions"]
        _state["message_data_dimensions"] = self.state["message_data_dimensions"]
        _state["tmp_data_dimensions"] = self.state["tmp_data_dimensions"]
        
         
        _state["message_data"] = list(self.state["message_data"])
        _state["tmp_data"] = list(self.state["tmp_data"])
        _state["data"] = list(self.state["data"])

        # Knowledge payloads
        _state["message_knowledge"] = list(self.state["message_knowledge"])
        _state["knowledge"] = list(self.state["knowledge"])
        _state["tmp_knowledge"] = list(self.state["tmp_knowledge"])

        # Cycle counters
        _state["data_mining_cycle"] = self.state["data_mining_cycle"]
        _state["knowledge_mining_cycle"] = self.state["knowledge_mining_cycle"]
        
        
        # Final response (serialized if present)
        if self.state["final_response"] is None:
            _state["final_response"] = None
        else:
            _state["final_response"] = dumpd(self.state["final_response"])

        # Response scores
        _state["response_scores"] = self.state["response_scores"]
        
        return _state
    
    @classmethod
    def from_dict(cls, data: Dict, thread_id: str): 
        ## Concept --> need to improve with firestore
        agent = cls(user=data["state"]["user_id"], thread_id=thread_id)
        agent.import_state(_state=data["state"])
        return agent

    def reset(self):
        """Reinitializing current state"""
        self.state = self._initialize_state()

    def update_state(self, state: AIState):
        """Merge current state with incoming state dictionary (for incremental updates)."""
    
        for key, value in state.items():
            if key == "conversation_history":
                for msg_dict in value:
                    self.state["conversation_history"].append(load(msg_dict))
            elif key == "message_tool_messages":
                for msg_dict in value:
                    self.state["message_tool_messages"].append(load(msg_dict))
            elif key in {"last_user_message", "last_ai_message"}:
                self.state[key] = load(value)
            else:
                self.state[key] = value
    
        return self.state

    def import_state(self, _state: AIState):
        """Replace current state (AIState) by provided state (AIState)"""
        chat_history: List[BaseMessage] = []
        for msg_dict in _state["conversation_history"]:
            chat_history.append(load(msg_dict))
            
        message_tool_messages: List[ToolMessage] = []
        for msg_dict in _state["message_tool_messages"]:
            message_tool_messages.append(load(msg_dict))
    
        self.state = AIState(
            thread_id=_state["thread_id"],
            user_id=_state["user_id"],
            session_last_updatedAt=_state["session_last_updatedAt"],

            conversation_history=chat_history,
            last_user_message=load(_state["last_user_message"]),
            last_ai_message=load(_state["last_ai_message"]),
            message_tool_messages=message_tool_messages,

            message_role_scores=_state["message_role_scores"],
            dominant_role=_state["dominant_role"],
            intent_scores=_state["intent_scores"],
            dominant_intent=_state["dominant_intent"],
            message_features=_state["message_features"],

            clarification_prompt=_state["clarification_prompt"],
            is_clarification_turn=_state["is_clarification_turn"],
            clarification_depth=_state["clarification_depth"],

            active_flow_label=_state["active_flow_label"],

            issues=_state["issues"],
            tmp_issues=_state["tmp_issues"],

            target_data_dimensions=_state["target_data_dimensions"],
            message_data_dimensions=_state["message_data_dimensions"],
            tmp_data_dimensions=_state["tmp_data_dimensions"],

            message_data=_state["message_data"],
            tmp_data=_state["tmp_data"],
            data=_state["data"],

            message_knowledge=_state["message_knowledge"],
            knowledge=_state["knowledge"],
            tmp_knowledge=_state["tmp_knowledge"],

            data_mining_cycle=_state["data_mining_cycle"],
            knowledge_mining_cycle=_state["knowledge_mining_cycle"],

            final_response=_state["final_response"],
            response_scores=_state["response_scores"]
        )
    
        return self.state

    async def invoke(self, prompt: str) -> BaseMessage:
        prompt_obj = HumanMessage(content=prompt)
        # Reset per-message state
        self.new_prompt_clear()
        self.set_last_user_message(prompt_obj)
        
        # Append user message to history
        self.state["conversation_history"].append(prompt_obj)
        
        final_state = await self.graph.invoke(self.state)
        ai_msg = final_state["final_response"]
        self.state["conversation_history"].append(ai_msg)
        
        return ai_msg
        
        
    def get_existing_message_list(self):
        """Return all messages within this agent / thread"""
        filtered = [
            msg for msg in self.state["conversation_history"]
            if isinstance(msg, (HumanMessage, AIMessage)) or
            (isinstance(msg, ToolMessage) and not getattr(msg, 'tool_calls', []))
        ]
        return dumpd(filtered)

    def set_last_user_message(self, user_message: HumanMessage):
        """
        Set last_user_message
        """
        self.state["last_user_message"] = user_message
    
    def finalize_ai_response(self, state: AIState, ai_message: Optional[AIMessage]):
        state["last_ai_message"] = ai_message
        state["final_response"] = ai_message
        
        state["session_last_updatedAt"] = datetime.now()
        
        ## do evaluation if needed, no evaluation here
        state["response_scores"] = None 
        
        return state
    
    # def process_new_data(self, data: Dict):
    #     """Append data to `tmp_data` & `data`"""
        
    #     deid_data = self.deid(data=data)
        
    #     self.state["data"].append(data)
    #     self.state["tmp_data"].append(data)
        
    # def process_new_knowledge(self, knowledge: Dict):
    #     """Append knowledge to `tmp_knowledge` & `knowledge`"""
        
    #     self.state["knowledge"].append(knowledge)
    #     self.state["tmp_knowledge"].append(knowledge)

    # ROUTING LOGIC
    def add_nodes(self, graph: StateGraph) -> StateGraph:
        """
        Assign all the nodes with names
        """
        graph.add_node("intent", self.intent)
        graph.add_node("analysis", self.analysis)
        graph.add_node("health_redirect", self.health_redirect)
        
        tool_node = ToolNode(list(self.tools.values()))
        graph.add_node("tools", tool_node)
        return graph
    
    def analyze_or_redirect(self, state: AIState):
        """
        Determine whether to analyze or respond a refocus message from current state.
        
        Returns:
            LangGraph Node || str: Node to proceed to
        """
        
        role_scores = state.get("message_role_scores", {})
        dominant_role = state.get("dominant_role", "")
        
        health_roles = ["query", "context"]
        non_analysis_roles = ["casual", "non-health", "vague"]
        threshold_margin = 0.15  # adjust as needed

        if dominant_role in non_analysis_roles:
            dominant_score = role_scores.get(dominant_role, 0.0)
            max_health_score = max((role_scores.get(r, 0.0) for r in health_roles), default=0.0)

            # Check how close the best health score is to the dominant one
            if (dominant_score - max_health_score) < threshold_margin:
                self.logger.info(
                    f"[ANALYZE_OR_REDIRECT] Ambiguous input: {dominant_role}={dominant_score:.2f}, "
                    f"closest health role={max_health_score:.2f}. Proceeding to analysis."
                )
                return "analysis"

            self.logger.info(
                f"[ANALYZE_OR_REDIRECT] Clear non-analysis input (role: {dominant_role}, score: {dominant_score:.2f}). Redirecting."
            )
            return "health_redirect"

        # Default: dominant role is already health-relevant
        return "analysis"
    
    # ROUTING LOGIC
    def has_analysis_need(self, state: AIState): 
        """
        Determine which resource is needed, which is exhausted, or nothing is needed
        
        Returns:
            LangGraph Node || str: Node to proceed to
        """
        
        # Check if any tool calls exists
        # if yes, go to `tools`
        if state["final_response"].tool_calls:
            return "tools"
        
        # if no, go to `normalize_response`
        return "normalize_response"
        
    def add_edges(self, graph: StateGraph) -> StateGraph:
        """
        Link predefined nodes together
        """
        try:
            graph.set_entry_point("intent")
            
            # Phase 1: Determine intent
            graph.add_conditional_edges("intent", self.analyze_or_redirect, ["analysis", "health_redirect"]) 
            
            # Phase 2: Determine analysis need
            ## analysis --> tools || normalize_response
            graph.add_conditional_edges("analysis", self.has_analysis_need, ["tools", END])
            graph.add_edges("tools", "analysis")
            
            graph.add_edge("health_redirect", END)
            
            return graph
        except Exception as e:
            self.logger.error("Failed to link nodes together. Make sure the nodes have been setup: ", str(e))
    
    def build_graph(self):

        """
        Construct LangGraph
        """

        try:
            builder = StateGraph(AIState)
    
            builder = self.add_nodes(graph=builder)
            builder = self.add_edges(graph=builder)
    
            memory = MemorySaver()
            graph = builder.compile(checkpointer=memory)
            return graph
        except Exception as e:
            self.logger.error("Failed to build graph: ", str(e))

    # NLP Helper function
    def _format_message_features_paragraph(self, features: Dict) -> str:
        
        """Convert message feature readings to a textual paragraph"""
        factual = features.get("factual", {})
        motivational = features.get("motivational", {})

        facts = []
        if factual.get("has_question"):
            facts.append("The user asked a question.")
        if factual.get("has_symptom"):
            facts.append("The user mentioned a symptom.")
        if factual.get("has_medical_term"):
            facts.append("The user used medical terminology.")

        motives = []
        if motivational.get("asks_what_if"):
            motives.append("The user is exploring a hypothetical or what-if scenario.")
        if motivational.get("seeks_community_comparison"):
            motives.append("The user is comparing their situation to others.")
        if motivational.get("is_self_reflective"):
            motives.append("The user is reflecting on their own condition or choices.")
        if motivational.get("seeks_confirmation"):
            motives.append("The user is seeking reassurance or validation.")

        paragraphs = []
        if facts:
            paragraphs.append("Factual signals detected:\n- " + "\n- ".join(facts))
        if motives:
            paragraphs.append("Motivational signals detected:\n- " + "\n- ".join(motives))

        return "\n\n".join(paragraphs) if paragraphs else "No strong factual or motivational features detected."

    ## NLP Helper function
    def summarize_data(self, state: AIState) -> str:
        """Convert Data Field of `state` to textual prompt"""
        data = state["data"]

        def recursive_parsing(d: dict, indent: int = 0) -> str:
            lines = []
            indent_str = "  " * indent

            for key, value in d.items():
                pretty_key = key.replace("_", " ").capitalize()

                if isinstance(value, dict):
                    lines.append(f"{indent_str}{pretty_key}:")
                    lines.append(recursive_parsing(value, indent + 1))
                else:
                    lines.append(f"{indent_str}- {pretty_key}: {value}")

            return "\n".join(lines)

        if not data:
            return "(No personal data available.)"

        str_data = "\n\n".join(
            [f"📄 Entry {i + 1}:\n{recursive_parsing(datum)}" for i, datum in enumerate(data)]
        )
        return f"Collected Personal Health Data:\n{str_data}"
        
    ## NLP Helper function
    def summarize_knowledge(self, state: AIState, indent: int = 0) -> str:
        """Convert Data Field of `state` to textual prompt"""
        knowledge = state.get("knowledge", [])
        indent_str = "  " * indent

        def recursive_parsing(d: dict, level: int = 0) -> str:
            lines = []
            prefix = "  " * level
            for key, value in d.items():
                pretty_key = key.replace("_", " ").capitalize()
                if isinstance(value, dict):
                    lines.append(f"{prefix}{pretty_key}:")
                    lines.append(recursive_parsing(value, level + 1))
                else:
                    lines.append(f"{prefix}- {pretty_key}: {value}")
            return "\n".join(lines)

        if not knowledge:
            return f"{indent_str}(No knowledge retrieved yet.)"

        blocks = [
            f"{indent_str}📚 Entry {i + 1}:\n{recursive_parsing(entry, indent + 1)}"
            for i, entry in enumerate(knowledge)
        ]
        return f"{indent_str}Retrieved Knowledge:\n" + "\n\n".join(blocks)
        

    ## Future: Modularize
    def deid(self, data: Any) -> Any:
        """Deidentify aggregated data"""
        redacted_fields = []

        def redact_recursive(obj: Any) -> Any:
            if isinstance(obj, str):
                original = obj
                obj = re.sub(r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", "[MY_NAME]", obj)
                obj = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[MY_EMAIL]", obj)
                obj = re.sub(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b", "[MY_PHONE]", obj)
                if obj != original:
                    redacted_fields.append(original)
                return obj
            elif isinstance(obj, dict):
                return {k: redact_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [redact_recursive(item) for item in obj]
            else:
                return obj

        return redact_recursive(data), redacted_fields

    ## NODE
    async def health_redirect(self, state: AIState) -> AIState:
        """
        * Guide user back to health discussion OR Ask user to be more specific
        """
        
        state["active_flow_label"].append(self.health_redirect.__name__)
        
        non_analysis_roles = ["casual", "non-health", "vague"]
        non_analysis_scores = {
            role: state["message_role_scores"].get(role, 0.0)
            for role in non_analysis_roles
        }

        redirect_prompt = HumanMessage(content=(
            f"The user's message was evaluated as likely being casual or ambiguous.\n"
            f"The following are the scores for each non-analysis category:\n"
            f"{json.dumps(non_analysis_scores, indent=2)}\n\n"
            f"{json.dumps(non_analysis_scores, indent=2)}\n\n"
            "Write a short message to the user:\n"
            "- If the scores suggest the user is being casual, acknowledge them and offer help.\n"
            "- If the scores suggest message as unrelated to health, gently redirect them back to health topics.\n"
            "- If the scores suggest message is vague and no clear goal embedded, ask a clarifying question so you can assist better.\n"
            "\n"
            "Respond directly to the user. Avoid over-apologizing. Be brief, supportive, helpful, and human."
        ))
        
        ## AIMessage
        response = await self.llm_pure.invoke(state["conversation_history"] + [redirect_prompt]) 
        state = self.finalize_ai_response(state=state, ai_message=response)

        return state

    async def invoke_with_json_retry(
                                        self,
                                        llm,
                                        messages: List[BaseMessage],
                                        max_retries: int = 2,
                                        json_only_instruction: str = (
                                            "Sorry, I didn’t get valid JSON. "
                                            "Please respond *only* with the JSON object and no extra text."
                                        )
                                    ) -> BaseMessage:
        """
        Generic JSON-retry wrapper for both ToolMessage and AIMessage responses.
        """
        combined = list(messages)
        for attempt in range(max_retries + 1):
            response = await llm.invoke(combined)
            try:
                _ = json.loads(response.content)
                return response
            except json.JSONDecodeError:
                self.logger.warning(f"[JSON RETRY] {attempt+1}/{max_retries+1} failed:\n{response.content}")
                if attempt < max_retries:
                    combined.append(HumanMessage(content=json_only_instruction))

        raise ValueError("Unable to obtain valid JSON after retries")
    
    ## NODE
    async def intent(self, state: AIState) -> AIState:
        """
        * Determine message features (consist of question? clarification? etc.)
        * Determine content focus, called intent here (is it personal? general? symptomatic?)
        * Determine message role, type of content type of content provided. (is it additional context? casual “hi”? non-health? query / question?)
        
        Output Expectation: 
        {
            "message_role_scores": {
                "query": float,
                "casual": float,
                "context": float,
                "non-health": float,
                "vague": float
            },
            "intent_scores": {
                "personal": float,
                "symptomatic": float,
                "hypothetical": float,
                "generic": float
            },
            "message_features": {
                "factual": {
                    "has_question": bool,
                    "has_symptom": bool,
                    "has_medical_term": bool,
                    "has_lifestyle": bool
                },
                "motivational": {
                    "ask_what_if": bool,
                    "seek_comparison": bool,
                    "seek_confirmation": bool,
                    "is_self_reflective": bool
                }
            }
        }
        """
        state["active_flow_label"].append(self.intent.__name__)
        
        evaluation_prompt = HumanMessage(content=(
                "You are evaluating a user message in the context of a health assistant chat.\n\n"
                "Analyze the latest user message and return a JSON structure with the following:\n\n"
                "1. **message_role_scores** – How likely (0.0 - 1.0) is this message to be each type?\n"
                "   - 'query': a clear health-related question.\n"
                "   - 'casual': a social or friendly message (e.g., 'hi', 'how are you').\n"
                "   - 'context': added detail about the user's health or situation without asking a question.\n"
                "   - 'non-health': about unrelated topics (e.g., weather, politics).\n"
                "   - 'vague': unclear or ambiguous (e.g., 'I feel weird today').\n\n"
                "2. **intent_scores** – What is the probability (0.0 - 1.0) of the main goal of the user?\n"
                "   - 'personal': seeking personalized reasoning based on their health.\n"
                "   - 'symptomatic': describing symptoms that may point to a condition.\n"
                "   - 'hypothetical': exploring a what-if scenario or health prediction.\n"
                "   - 'generic': general curiosity about health topics or terms.\n\n"
                "3. **message_features** – Boolean flags for what’s in the message.\n"
                "   - factual: { has_question, has_symptom, has_medical_term, has_lifestyle }\n"
                "   - motivational: { ask_what_if, seek_comparison, seek_confirmation, is_self_reflective }\n\n"
                "Return your result strictly as a JSON object in the format:\n"
                "{\n"
                "  \"message_role_scores\": { ... },\n"
                "  \"intent_scores\": { ... },\n"
                "  \"message_features\": { \"factual\": {...}, \"motivational\": {...} }\n"
                "}"
        ))

        response = await self.llm_pure.invoke(state["conversation_history"] + [evaluation_prompt])
        
        # Parse the Response
        try:
            scores_and_flags = json.loads(response.content)
        except json.JSONDecodeError as e:
            # Handle Parsing Error
            self.logger.error(f"[INTENT] Failed to parse LLM response into JSON: {str(e)}\nRaw response:\n{response.content}")
            raise ValueError(f"Failed to parse LLM response into JSON: {str(e)}")
        
        required_keys = ["message_role_scores", "intent_scores", "message_features"]
        if not all(k in scores_and_flags for k in required_keys):
            self.logger.warning(f"[INTENT] Parsed JSON missing expected keys: {list(scores_and_flags.keys())}")

        
        ## Updating the states
        state["message_role_scores"] = scores_and_flags.get("message_role_scores", {})
        state["dominant_role"] = max(
            scores_and_flags.get("message_role_scores", {}),
            key=scores_and_flags.get("message_role_scores", {}).get,
            default=None
        )
        state["intent_scores"] = scores_and_flags.get("intent_scores", {})
        state["dominant_intent"] = max(
            scores_and_flags.get("intent_scores", {}),
            key=scores_and_flags.get("intent_scores", {}).get,
            default=None
        )
        state["message_features"] = scores_and_flags.get("message_features", {})
        
        return state
    
    ## Analysis Helper function
    def update_issues(self, state: AIState, issues: List[str]) -> AIState:
        """Update issue states"""
        
        state["tmp_issues"].clear()
        state["tmp_issues"].extend(issues)
        state["issues"].append(issues)
        return state
       
    ## Analysis Helper function
    async def process_tool_message(self, state: AIState, tool_message: ToolMessage) -> AIState:
        """
        Parse the LLM's JSON output in `tool_message.content` and update `state` accordingly.

        Expected JSON schema:
        {
            "issues": [<str>, ...],
            "data_need": bool,
            "knowledge_need": bool,
            "clarification_need": bool,
            "output_ready": bool,
            "specs": <dict or list>
        }
        Exactly one of the *_need/output flags must be True.

        Updates include:
        - Recording new issues via `update_issues`
        - Incrementing/resetting cycle counters
        - Storing `specs` into appropriate state fields
        - Clearing temporary buffers (tmp_data, tmp_knowledge)
        - For clarification or output, firing `finalize_ai_response`
        """
        
        state["message_tool_messages"].append(tool_message)
            
        # 1. Load and validate JSON
        try:
            payload = json.loads(tool_message.content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}\nRaw content: {tool_message.content}")
            raise ValueError(f"Invalid JSON in tool message: {e}")

        # 2. Identify active flag
        flags = ["data_need", "knowledge_need", "clarification_need", "output_ready"]
        active = [f for f in flags if payload.get(f) is True]
        if len(active) != 1:
            self.logger.error(f"Expected one active flag; got {active}")
            raise ValueError(f"One of {flags} must be True, found: {active}")
        flag = active[0]
        
        ## CHECKING NO INCONSISTENT TOOL TYPES
        # 1) Filter calls by phase
        orig_calls = tool_message.tool_calls
        if flag == "data_need":
            valid_calls = [c for c in orig_calls if c.tool_name.startswith("data.")]
        elif flag == "knowledge_need":
            valid_calls = [c for c in orig_calls if c.tool_name.startswith("knowledge.")]
        else:
            valid_calls = []  # clarification/output shouldn’t have tool calls

        tool_message.tool_calls = valid_calls

        # 2) If that filtering stripped everything out, auto‑retry the LLM
        if not valid_calls and flag in ("data_need", "knowledge_need"):
            self.logger.warning(f"[ANALYSIS] Mixed or missing tool calls for {flag}; auto‑retrying LLM.")
            # Small “hint” to the model: only emit calls of the one phase
            hint = (
                f"In your last response you tried to call both data and knowledge tools. "
                f"Please reply again in JSON with *only* the tool calls relevant to the single phase '{flag}'."
            )
            # Re‑run the analysis prompt, injecting that hint at the end:
            follow_up = state["conversation_history"] + [HumanMessage(content=hint)]
            response2 = await self.invoke_with_json_retry(
                llm=self.llm_with_tools,
                messages=follow_up,
                max_retries=1,
            )
            # And recurse: parse it as if it were the original response
            return await self.process_tool_message(state, response2)

        # 3. Ensure specs present
        if "specs" not in payload:
            self.logger.error("Missing 'specs' in payload.")
            raise ValueError("Missing 'specs' field")
        specs = payload["specs"]
 
        # 4. Update issues
        issues = payload.get("issues", [])
        state = self.update_issues(state, issues)
        
        # 5. Handle each flag
        def finalize_from_specs(specs: dict):
            # Extract the user-facing message
            user_content = specs.get("content", "")
            ai_msg = AIMessage(
                content=user_content,
                additional_kwargs={
                    "data": state.get("message_data", []),
                    "knowledge": state.get("message_knowledge", [])
                }
            )
            return self.finalize_ai_response(state, ai_msg)

        if flag == "data_need":
            # specs must be dict of {"data.provider.datatype": "reason"}
            if not isinstance(specs, dict):
                self.logger.error("[ANALYSIS] data_need specs must be a dict")
                raise ValueError("data_need specs must be a dict")
            for key, reason in specs.items():
                if not key.startswith("data.") or not isinstance(reason, str):
                    self.logger.error(f"[ANALYSIS] Invalid data_need entry: {key}: {reason}")
                    raise ValueError(f"Invalid data_need entry: {key}: {reason}")
            # update state
            state["target_data_dimensions"] = specs
            state["data_mining_cycle"] += 1
            state["knowledge_mining_cycle"] = 0
            state.get("tmp_data", []).clear()
        elif flag == "knowledge_need":
            # specs must be dict of {"knowledge.provider": (prompt, reason)}
            if not isinstance(specs, dict):
                self.logger.error("[ANALYSIS] knowledge_need specs must be a dict")
                raise ValueError("knowledge_need specs must be a dict")
            for provider, pair in specs.items():
                if not provider.startswith("knowledge."):
                    self.logger.error(f"[ANALYSIS] Invalid provider key: {provider}")
                    raise ValueError(f"Invalid provider key: {provider}")
                if (not isinstance(pair, (list, tuple))) or len(pair) != 2:
                    self.logger.error(f"[ANALYSIS] Invalid knowledge_need value for {provider}: {pair}")
                    raise ValueError(f"Invalid knowledge_need value for {provider}: {pair}")
                prompt, reason = pair
                if not all(isinstance(x, str) for x in (prompt, reason)):
                    self.logger.error(f"[ANALYSIS] Both prompt and reason must be strings for {provider}")
                    raise ValueError(f"Both prompt and reason must be strings for {provider}")
            state["knowledge_mining_cycle"] += 1
            state.get("tmp_knowledge", []).clear()

        elif flag == "clarification_need":
            # specs must be list of dicts with required keys
            if not isinstance(specs, list):
                self.logger.error("[ANALYSIS] clarification_need specs must be a list")
                raise ValueError("clarification_need specs must be a list")
            for item in specs:
                if not isinstance(item, dict) or \
                not all(k in item for k in ["clarification_question", "clarification_reason"]):
                    self.logger.error(f"[ANALYSIS] Invalid clarification item: {item}")
                    raise ValueError(f"Invalid clarification item: {item}")
            state["clarification_prompt"] = specs
            state["is_clarification_turn"] = True
            state["clarification_depth"] = state.get("clarification_depth", 0) + 1
            return finalize_from_specs(specs=specs)

        elif flag == "output_ready":
            # specs must contain 'content'
            if not isinstance(specs, dict) or 'content' not in specs:
                self.logger.error("[ANALYSIS] output_ready specs must be a dict with 'content'")
                raise ValueError("output_ready specs must be a dict with 'content'")
            return finalize_from_specs(specs=specs)

        else:
            self.logger.error(f"[ANALYSIS] Unrecognized flag: {flag}")
            raise ValueError(f"[ANALYSIS] Unrecognized flag: {flag}")
        
        return state
        
       
    ## NODE 
    async def analysis(self, state: AIState) -> AIState:
        """
        Given `state` conforming to AIState TypedDict, this node will:
        1. Extract `last_user_message`, `message_features`, `intent_scores`,
            `data_mining_cycle`, `knowledge_mining_cycle`, and `target_data_dimensions`.
        2. Identify core issues (`issues`) from `last_user_message`.
        3. Determine which flag to set (mutually exclusive):
            - `data_need` (requires more user data)
            - `knowledge_need` (requires external knowledge lookup)
            - `clarification_need` (requires user clarification)
            - `output_ready` (ready to summarize or exhaust)
        4. Populate `state` fields:
            - Append this node name to `active_flow_label`.
            - Update `state['final_response']` with the LLM's ToolMessage.

        Transition rules (enforced in-prompt):
        - If `knowledge_mining_cycle` ≥ 3 → force `clarification_need`.
        - If `data_mining_cycle` ≥ 3 → skip to `knowledge_need`, reset future data cycles.
        - If Generic intent is highest in `intent_scores` → skip data, perform only `knowledge_need`.

        Upon completion, `state` will include:
        - Updated `active_flow_label` (list of node names).
        - `final_response`: ToolMessage whose JSON payload contains:
            {"issues": [...], "data_need": bool, "knowledge_need": bool,
            "clarification_need": bool, "output_ready": bool, "specs": {...}}
        """
        
        state["active_flow_label"].append(self.analysis.__name__)
        # Extract relevant state
        user_msg = state.get('last_user_message').content if state.get('last_user_message') else ''
        intents = state.get("intent_scores") or {"personal":0,"symptomatic":0,"hypothetical":0,"generic":0}
        features = state.get("message_features") or {"factual":{}, "motivational":{}}
        data_cycle = state.get('data_mining_cycle', 0)
        know_cycle = state.get('knowledge_mining_cycle', 0)
        collected = state.get('target_data_dimensions', {})

        # Override logic
        is_generic = intents.get('generic', 0) >= max(intents.values(), default=0)
        # force_clarify = know_cycle >= 3
        # force_knowledge = data_cycle >= 3 or is_generic

        # Log override decisions
        self.logger.debug(f"[ANALYSIS] Cycles: data={data_cycle}, knowledge={know_cycle}, generic={is_generic}")
        
        ## Preprocessing
        ## Aggregate data and clear buffer
        # Merge new data and clear buffer
        for datum in state.setdefault("tmp_data", []):
            state["data"].append(datum)
            state["message_data"].append(datum)
        state["tmp_data"].clear()
        # Merge new knowledge and clear buffer
        for item in state.setdefault("tmp_knowledge", []):
            state["knowledge"].append(item)
            state["message_knowledge"].append(item)
        state["tmp_knowledge"].clear()
        
        # PROMPT SECTIONS (normalize indentation)
        context = (
            "User Message:\n"
            f"{user_msg}\n\n"
            "Message Features:\n"
            f"{self._format_message_features_paragraph(features)}\n\n"
            "Intent Scores:\n"
            f"{', '.join(f'{k}: {v:.2f}' for k,v in intents.items())}"
        )
        status = (
            f"Data Cycles: {data_cycle}\n"
            f"Knowledge Cycles: {know_cycle}\n"
            "Collected Data Dimensions:\n"
            f"{chr(10).join(f'- {k}: {v}' for k, v in collected.items())}"
        )
        rules = (
            "Decision Rules:\n"
            "1. If knowledge cycles ≥ 3 → clarification_need.\n"
            "2. If data cycles ≥ 3 → knowledge_need.\n"
            "3. If generic highest → knowledge_need only.\n"
            "4. Else choose one based on top scoring intent: data_need, knowledge_need, clarification_need, or output_ready.\n"
            "If there is a tie in intent scores or dominant intent score is no more than 0.5 different from second place, "
            "ask a clarification question.\n"
            "Only one flag may be True but you can always select multiple tools of the same type "
            "(e.g. multiple data.<provider>.<datatype> for data_need). Avoid repeating collected data."
        )
        output_fmt_schema = (
            "Respond in JSON:\n"
            "{\n"
            "  \"issues\": [...],\n"
            "  \"data_need\": bool,\n"
            "  \"knowledge_need\": bool,\n"
            "  \"clarification_need\": bool,\n"
            "  \"output_ready\": bool,\n"
            "  \"specs\": { ... }\n"
            "}\n\n"
            "Specs mapping:\n"
            "- data_need: {\"data.<provider>.<datatype>\": \"<reason>\", ...}\n"
            "- knowledge_need: {\"knowledge.<provider>\": [\"<prompt>\", \"<reason>\"], ...}\n"
            "- clarification_need: [{\"clarification_question\": \"...\", \"clarification_reason\": \"...\"}, ...]\n"
            "- output_ready: {\"content\": \"...\"}"
        )
        output_fmt_notes = (
            "After the JSON, when output_ready is true, clearly present information into sections and format the user message "
            "into clearly demarcated sections. E.g., use **bold** for headings, *italic* for emphasis."
        )
        prompt = "\n---\n".join([context, status, rules, output_fmt_schema, output_fmt_notes])
        
        # Log prompt
        self.logger.debug(f"[ANALYSIS] Prompt sent: {prompt}")


        # Invoke
        tmp_messages = state["conversation_history"] + [HumanMessage(content=prompt)]
        response = await self.invoke_with_json_retry(llm=self.llm_with_tools, messages=tmp_messages)
        state = await self.process_tool_message(state=state, tool_message=response)        
        # Log response
        self.logger.debug("[ANALYSIS] Received response: %s", response.content)
        state['final_response'] = response
        return state
    

    @tool(name="data.whoop", description="Fetch WHOOP wearable data by type (e.g. sleep, heart_rate, recovery).")
    async def fetch_whoop(self, _type: str, reason: str) -> Dict:
        """
        DATA FUNCTION: fetch data from WHOOP data provider, called when 'data.whoop.<datatype>' is selected. **Will Update the State by Class Function**

        Available Datatypes:
        1. sleep
        2. cycle
        3. user
        4. body_measurements

        Args: 
            _type (str): determining which type of data need to be retrieved from WHOOP API, aka the <datatype> in `data.whoop.<datatype>`

        Returns:
            dict: A dictionary containing targeted data extract from WHOOP account
                if an error encountered, return empty dict 
        """
        try:
            ## TODO
            
            WHOOP_UTILS_MAPPER = {
                # "sleep":
                # "cycle": 
                # "user": 
                # "body_measurements": 
            }
            
            ## TEST DATA
            
            if _type == "sleep":
                data = [{"type": "sleep", "rem_minutes": 120, "total_minutes": 410}]
            elif _type == "cycle":
                data = [{"type": "cycle", "heart_rate": 80}]
            elif _type == "body_measurements":
                data = [{"type": "body_measurements", "weight": 55, "height": 175}]
            else: 
                data = []
                
            data = self.deid(data=data)
            ## Key must match target variable name
            return {
                "data": data,
                "tmp_data": data,
                "message_data": data,
                "active_flow_label": self.fetch_whoop.__name__
            }
        except Exception as e:
            self.logger.warning("[FETCH WHOOP] Failed to fetch WHOOP data: %s", str(e))
            return {}

    @tool(name="data.vector", description="Fetch manually uploaded document data with similarity algorithm.")
    async def fetch_vector(self) -> Dict:
        """
        DATA FUNCTION: fetch data through RAG from vector database, called when 'data.vector.<datatype>' is selected. **Will Update the State by Class Function**
        
        Args:
            None
        
        Returns:
            dict: A dictionary containing top 5 most similar health document chunks found in vector database 
                if an error encountered or no document found, return empty dict
        """
        try: 
            ## TODO
            # relevant_docs = query_docs_from_chroma(
            #     prompt=self.state["last_user_message"],
            #     premise={
            #         "user_id": self.user_id
            #     }
            # )
            
            # self.process_new_data(relevant_docs)
            
            ## TEST DATA
            return {
                "active_flow_label": self.fetch_vector.__name__
            }
        except Exception as e:
            self.logger.warning("[FETCH VECTOR] Failed to fetch vector database document chunks: %s", str(e))
            return {}

    # @tool
    # async def fetch_EPIC(self, user_id: str) -> Dict:
    #     """
    #     Function to fetch data from electronic health record system. **Will Update the State by Class Function**

    #     Args:
    #         user_id (str): identifying user and their connected EPIC account. If no user id or no EPIC account connected, throw an error.

    #     Returns:
    #         dict: A dictionary containing targeted data extract from WHOOP account
    #             if an error encountered, return empty dict
    #     """

    #     try:

    #     except Exception as e:
    #         self.logger.error("Failed to fetch EPIC data: %s", str(e))
    #         return {}

    @tool(name="knowledge.tavily", description="Search health knowledge for confident response.")
    async def search_tavily(self) -> Dict:
        """
        KNOWLEDGE FUNCTION: conduct web search on concerns, called when 'knowledge.tavily' is selected. **Will Update the State by Class Function**

        Returns:
            dict: A dictionary containing search results from Tavily. It follows the format below: 
                {
                  "query": "Who is Leo Messi?",
                  "images": [
                    {
                      "url": "Image 1 URL",
                      "description": "Image 1 Description",
                    },
                    ...
                  ],
                  "results": [
                    {
                      "title": "Source 1 Title",
                      "url": "Source 1 URL",
                      "content": "Source 1 Content",
                      "score": 0.99
                    },
                    ...
                  ],
                  "response_time": 1.09
                }

                if error encountered, return empty dict
        """

        try:
            ## TODO
            ## TEST DATA
            knowledge = {"content": "coffee is good. end of discussion."}
            
            return {
                "knowledge": knowledge,
                "tmp_knowledge": knowledge,
                "message_knowledge": knowledge,
                "active_flow_label": self.search_tavily.__name__
            }
        except Exception as e:
            self.logger.warning("[SEARCH TAVILY] Failed to search Tavily: %s", str(e))
            return {}