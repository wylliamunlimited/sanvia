import json
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph, END

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.messages.tool import ToolMessage

from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool
from langchain_core.load import load, dumpd

## Parallelism
import operator

from typing import TypedDict, List, Dict, Mapping, Optional, Tuple, Annotated, Any, Union
from datetime import datetime


class AIState(TypedDict):
    # --- [NON-CHAT SPECIFIC] Identification ---
    thread_id: str
    user_id: str
    session_last_updatedAt: datetime
    
### + --------------------- WILL BE IMPLEMENTED IN AGENT CLASS --------------------- +
    
    # user_level: Optional[str]                  ## default: "beginner" (don't know how to approach information at all)
    #                                            ##          "informed" (know that information is not to be fully transferrable to daily practice)
    #                                            ##          "expert" (have a decent level of medical knowledge)
    #                                            ##          determining user's potential risk of misunderstanding material 
    
    # # --- [NON-CHAT SPECIFIC] Constants ** need to be predefined ** ---  
    # available_datatype: List[Tuple[str, str]]        ## listing available options for AI to choose, 
    #                                                 ## e.g. [("WHOOP", "Sleep"), ("EPIC", "Lab"), ...]
    # basic_user_profile: Dict                         ## data from onboarding 
    # favorable_scores: Mapping[str, float]            ## indicating which data provider is more used and attended to by user, ensuring data quality

### -------------------------------------------------------------------------------- +

    
    # --- Message Memory ---
    conversation_history: Annotated[List[BaseMessage], operator.add]          ## WHOLE CONVERSATION
                                            # "role": "system", "user", "assistant"
                                            # "content": "..."
                                            # "timestamp": datetime
                                            # "sources": [{...}, {...}, ...]
                                            # "personal_data": [{...}, {...}, ...]
    last_user_message: Optional[HumanMessage]         ## referencing ai message
    last_ai_message: Optional[AIMessage]              ## referencing user message
    message_tool_messages: Annotated[List[ToolMessage], operator.add]          ## referencing tool message





    
    # --- Soft Classification [MESSAGE SPECIFIC] ---
    message_role_scores: Optional[Mapping[str, float]]             ## "query" "context" "casual [no particular topic]" "non-health" "vague"
    dominant_role: Optional[str]                         ## "new_query" "context_enrich" "casual [no particular topic]" "non-health" ""
    intent_scores: Optional[Mapping[str, float]]                   ## "personal" "symptomatic" "hypothetical" "generic"
                                                # personal ==> show contrasts with existing literatures and other users
                                                # hypothetical ==> explore possibilities & what-if learning
                                                # generic ==> [LOWEST RISK] core educational, most straightforward
                                                # symptomatic ==> [HIGHEST RISK] acknowledge connections between diseases and symptoms
    dominant_intent: Optional[str]                       ## "personal" "symptomatic" "hypothetical" "generic"
    message_features: Optional[Dict[str, bool]]                    
                                                # "message_features": {
                                                #   "factual": {
                                                #     "has_question": bool,
                                                #     "has_symptom": bool,
                                                #     "has_medical_term": bool
                                                #   },
                                                #   "motivational": {
                                                #     "asks_what_if": bool,
                                                #     "seeks_community_comparison": bool,
                                                #     "is_self_reflective": bool,
                                                #     "seeks_confirmation": bool
                                                #   }
                                                # }



    
    # --- Flow Control --- 
    clarification_prompt: Optional[List[Dict]]                       ## MESSAGE SPECIFIC: Record & Explain desired clarification content
                                            # [{
                                            #     "clarification_question": "Could you tell me how long you've been experiencing this fatigue?",
                                            #     "clarification_reason": "This information will help determine whether the issue is acute, like a short-term illness, or chronic, which may suggest something more systemic.",
                                            #     "is_clarification_turn": true
                                            # }, ...]
    is_clarification_turn: Optional[bool]                      ## MESSAGE SPECIFIC: if True, the AI is expecting a response clarification from user
    clarification_depth: Optional[int]                         ## WHOLE CONVERSATION: counting loops how many rounds of detail mining




    
    # --- Logging ---
    active_flow_label: Annotated[List[str], operator.add]              ## MESSAGE SPECIFIC: list of LangGraph node experienced by message ** CLEAR WHEN ENTERING GRAPH




    
    # --- Information Extraction / NLP Analysis --- 
    issues: Annotated[List, operator.add]                                         ## WHOLE CONVERSATION: All symptoms, conditions, keywords mentioned in the conversation
    tmp_issues: Annotated[List, operator.add]                                     ## MESSAGE SPECIFIC: Extracted symptoms, conditions, keywords ** CLEAR WHEN ENTERING GRAPH




    
    
    # --- External Data (serving by organization, might not be scalable) ---
    target_data_dimensions: Mapping[str, str]                 ## MESSAGE SPECIFIC: Target data fields, e.g. ["data.whoop.sleep": "explaining sleep patterns"], 
                                                              ##       depending on existing available data providers offer ** CLEAR WHEN ENTERING GRAPH
    message_data_dimensions: Mapping[str, str]
    tmp_data_dimensions: Mapping[str, str]
    
    message_data: Annotated[List[Dict], operator.add]                      ## MESSAGE SPECIFIC: list of data for the entire message (does not get cleared every cycle)
    tmp_data: Annotated[List[Dict], operator.add]                          ## MESSAGE SPECIFIC: list of available data dictionary ** CLEAR WHEN ENTERING GRAPH
    data: Annotated[List[Dict], operator.add]                              ## WHOLE CONVERSATION: all data mined
                                        ## IMPORTANT: Include a field of `deidentified: Dict` for de-identification
                                            # "applied": bool
                                            # "censored_fields": List[str] // would be a series of predefined fields
                                            # "method": List[str] // list of method used

    data_mining_cycle: int
    # FUTURE
    # data_mining_cycle: Mapping[str, int]                    ## MESSAGE SPECIFIC: counting how many times data mining
    #                                         # {
    #                                         #     "whoop": 3,
    #                                         #     "vector": 3
    #                                         # }



    
    # --- Knowledge Search ---
    message_knowledge: Annotated[List[Dict], operator.add]                      ## MESSAGE SPECIFIC: list of knowledge for the entire message (does not get cleared every cycle)
    knowledge: Annotated[List[Dict], operator.add]
    tmp_knowledge: Annotated[List[Dict], operator.add]
    
    knowledge_mining_cycle: int
    # FUTURE
    # knowledge_mining_cycle: Mapping[str, int]                ## MESSAGE SPECIFIC: counting how many times knowledge search 
    #                                                          ## has been done using the same set of dataset ** CLEAR WHEN ENTERING GRAPH
    #                                         # {
    #                                         #     "tavily": 3
    #                                         # }





    
    # --- Final Response Layer ---
    final_response: Optional[Union[AIMessage, ToolMessage]]                        ## MESSAGE SPECIFIC: Final Response Message
    response_scores: Optional[Mapping[str, float]]       ## MESSAGE SPECIFIC: assess what intension the response is aiming ** CLEAR WHEN ENTERING GRAPH
                                               ##                   "educational_summary" "clarification_prompt" "casual_reply" 