import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

import json
from fastapi import HTTPException
from langchain_openai import ChatOpenAI
from constants.credentials import OPENAI_API_KEY
from constants.langgraph_obj import AIBrain
from dependencies.tavily_dependencies import tavily_intense_search
from langgraph.graph import START, StateGraph, END
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from dependencies.rag_dependencies import get_docs_from_chroma, query_docs_from_chroma
from dependencies.firebase_dependencies import get_firestore_client, get_profile
from dependencies.survey_rag import get_survey_context, get_bmi_context


def get_llm():
    """Return the LLM."""
    try:
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=OPENAI_API_KEY,
            max_retries=3,
        )
    except Exception as e:
        print(f"❌ Error initializing LLM: {str(e)}")
        raise


def determine_relevance(thoughts: AIBrain) -> AIBrain:
    """DECISION POINT FOR RELEVANCE

    Description
    -----------
    This node is responsible for determining if user's query is regarding to health.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """
    
    thoughts["data_extraction_completed"] = False

    session_history = thoughts["prompt_chain"]

    reconstructed_prompt = session_history + [
        {
            "role": "user",
            "content": (
                "Determine the relevance of the last user message to health, considering the conversation history.\n"
                "1. If the latest message is **explicitly about health**, return a relevance score between 0.5 and 1.\n"
                "2. If the latest message is **not health-related but follows a prior health discussion logically**, return a moderate score (0.3 - 0.6).\n"
                "3. If the latest message is **completely unrelated to health**, return a low score (0 - 0.3).\n"
                "4. If the latest message is a phatic expression ('hi', 'thank you', 'okay', 'how are you', etc.), return -1.\n"
                "Return **only a decimal value between 0 and 1**, with no additional text."
            ),
        }
    ]

    decision = get_llm().invoke(reconstructed_prompt)

    relevance_score = float(decision.content)
    thoughts["relevance"] = relevance_score

    # Track health mode
    if relevance_score >= 0.5:
        thoughts["health_mode"] = True
    elif relevance_score < 0.3:
        thoughts["health_mode"] = False

    return thoughts


def respond_manner(thoughts: AIBrain) -> AIBrain:
    """DECISION POINT FOR RESPONDING MANNER

    Description
    -----------
    This node is responsible for responding to polite message, like thank you or greetings.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """

    # print(f"🧠 AGENT: DECISION POINT - Responding to polite message 🧠")

    tmp_prompt = thoughts["prompt_chain"] + [
        {
            "role": "user",
            "content": (
                "Ask me what I need, but consider the context and health focus."
            ),
        }
    ]

    ai_question = get_llm().invoke(tmp_prompt)

    thoughts["prompt_chain"].append(
        {
            "role": "assistant",
            "content": ai_question.content,
            "references": thoughts.get("shortterm_knowledge", []),
        }
    )

    return thoughts


def refocus_medicine(thoughts: AIBrain) -> AIBrain:
    """REFOCUS NODE
    Description
    -----------
    This node is responsible for refocusing the LangGraph Agent to ask user to be more relevant to medicine.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent
    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """
    thoughts["prompt_chain"].append(
        {
            "role": "assistant",
            "content": "Let's circle back to medicine. What specific health-related question do you have?",
            "references": [],
        }
    )

    return thoughts


def enough_info_dec_pt(thoughts: AIBrain) -> AIBrain:
    """Decision Point for determining if there is enough information to proceed with the next steps.

    Parameters
    ----------
    thoughts : AIBrain
        State of the LangGraph Agent.

    Returns
    -------
    AIBrain
        State of the LangGraph Agent.
    """

    session_history = thoughts["prompt_chain"]
    user_messages = [
        message_obj for message_obj in session_history if message_obj["role"] == "user"
    ]
    stringified_user_messages = "\n".join(
        [message_obj["content"] for message_obj in user_messages]
    )
    
    reconstructed_prompt = [
        {
            "role": "user",
            "content": (
                stringified_user_messages
                + "\n"
                + "Is there enough information to proceed with a confident conclusion? "
                "Only answer strictly (without punctuation or space) 'yes' or 'no'. "
            ),
        }
    ]

    decision = get_llm().invoke(reconstructed_prompt)

    if decision.content == "yes":
        # print("🧠 AGENT: DECISION POINT - Proceeding with the next steps 🧠")
        thoughts["proceed"] = True
    elif decision.content == "no":
        # print("🧠 AGENT: DECISION POINT - Not enough information to proceed 🧠")
        # print(f"🧠 AGENT:       Evaluated {stringified_user_messages} 🧠")
        thoughts["proceed"] = False
    else:
        # print(
        #     "🧠 AGENT: DECISION POINT - Invalid response. Defaulting to not proceed. Value: ",
        #     decision.content,
        #     " 🧠",
        # )
        thoughts["proceed"] = False

    return thoughts

def enough_info_dec_pt_post_extract(thoughts: AIBrain) -> AIBrain:
    """Decision Point for determining if there is enough information (After system information retrieval) to proceed with the next steps.

    Parameters
    ----------
    thoughts : AIBrain
        State of the LangGraph Agent.

    Returns
    -------
    AIBrain
        State of the LangGraph Agent.
    """

    session_history = thoughts["prompt_chain"]
    user_messages = [
        message_obj for message_obj in session_history if message_obj["role"] == "user"
    ]
    stringified_user_messages = "\n".join(
        [message_obj["content"] for message_obj in user_messages]
    )
    total_content = ('User portfolio: ' +thoughts["data"]["survey_context"] + '\n' if thoughts["data"]["survey_context"] else "") + ('Documents: ' + thoughts["data"]["doc_context"] + '\n' if thoughts["data"]["doc_context"] else "") + stringified_user_messages
    
    reconstructed_prompt = [
        {
            "role": "user",
            "content": (
                total_content
                + "\n"
                + "Is there enough information to proceed with a confident conclusion? "
                "Only answer strictly (without punctuation or space) 'yes' or 'no'. "
            ),
        }
    ]

    decision = get_llm().invoke(reconstructed_prompt)

    if decision.content == "yes":
        # print("🧠 AGENT: DECISION POINT - Proceeding with the next steps after Data Extract 🧠")
        thoughts["proceed"] = True
    elif decision.content == "no":
        # print("🧠 AGENT: DECISION POINT - Not enough information to proceed after Data Extract 🧠")
        # print(f"🧠 AGENT:       Evaluated {total_content} 🧠")
        thoughts["proceed"] = False
    else:
        # print(
        #     "🧠 AGENT: DECISION POINT - Invalid response. Defaulting to not proceed. Value: ",
        #     decision.content,
        #     " 🧠",
        # )
        thoughts["proceed"] = False

    return thoughts

def generate_question(thoughts: AIBrain) -> AIBrain:
    """QUESTION GENERATION NODE
    Description
    -----------
    This node is responsible for generating a question to ask the user if there is not enough information to proceed.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """
    
    prefix_prompt = []
    if thoughts["data"]["survey_context"]:
        survey = {
            "role": "system",
            "content": thoughts["data"]["survey_context"],
        }
        prefix_prompt += [survey]
        
    if thoughts["data"]["doc_context"]:
        doc = {
            "role": "system",
            "content": thoughts["data"]["doc_context"],
        }
        prefix_prompt += [doc]

    tmp_prompt =  prefix_prompt + thoughts["prompt_chain"] + [
        {
            "role": "user",
            "content": (
                "Given my health context above, what other details do you need from me? Give me one question."
            ),
        }
    ]
    
    print()
    print(
        f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [START] 🧠 - - - - - - -\n{json.dumps(tmp_prompt, indent=4)}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [END] 🧠 - - - - - - -"
    )
    print()

    ai_question = get_llm().invoke(tmp_prompt)

    thoughts["prompt_chain"].append(
        {
            "role": "assistant",
            "content": ai_question.content,
            "references": thoughts.get("shortterm_knowledge", []),
        }
    )
    

    return thoughts

## IMPORTANT: this data extraction is conditional, depending on what is in "data" and what the user is asking
## there is also foundational data needed, so another separate logic is to find out which foundational data
##                                              is missing then call api to extract them
## if foundational data could not be retrieved, the status should also be noted in the data field, indicating
##                                              LLM tried to retrieve but failed
def data_extract(thoughts: AIBrain) -> AIBrain:
    """DATA EXTRACTION NODE
    Description
    -----------
    This node is responsible for searching across various system for user's health data.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """
    # Get user's documents from Firestore
    db = get_firestore_client()
    user_id = thoughts.get('user_id')
    if not user_id:
        print(f"User ID is not present -> {user_id}")
        raise 
    
    survey_data = get_profile(user_id=user_id)

    # Get survey data context
    survey_context = get_survey_context(survey_data=survey_data) ## stringified survey content
    if survey_context:
        thoughts["data"]["survey_context"] = survey_context
    
    # Get last message
    last_mess_content = thoughts["prompt_chain"][-1]["content"]
    
    # Get top 5 relevant document data from last message 
    relevant_docs = query_docs_from_chroma(
        prompt=last_mess_content,
        premise={
            "user_id": user_id
        }
    )
    
    # Flatten content of queried documents
    content = ' '.join([doc[0] for doc in relevant_docs["documents"]])
    if len(content.strip()) > 0:
        thoughts["data"]["doc_context"] = content
        
    # print(f" ===LANGGRAPH=== Doc Data: {thoughts['data']['doc_context']}")
        
        
    # print(
    #     f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: context [START] 🧠 - - - - - - -\n{json.dumps(thoughts['data'])}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: context [END] 🧠 - - - - - - -"
    # )

    return thoughts


def knowledge_gathering(thoughts: AIBrain) -> AIBrain:
    """INFORMATION GATHERING NODE

    Description
    -----------
    This node is responsible for gathering information from the internet to enrich the LangGraph Agent's knowledge base.

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """

    search_prompt = get_llm().invoke(
        thoughts["prompt_chain"]
        + [
            {
                "role": "user",
                "content": (
                    "Summarize the key points into a search query with a maximum of 400 characters. "
                    "This query will be used to search for relevant information on the internet."
                ),
            }
        ]
    )

    search_category = get_llm().invoke(
        thoughts["prompt_chain"]
        + [
            {
                "role": "user",
                "content": (
                    "Determine the category of the search query. "
                    "Strictly respond with one of the following categories: 'diagnosis', 'next_steps', 'research_papers'."
                ),
            }
        ]
    )

    # print(f"AGENT: search metadata => {search_prompt.content}, {search_category.content}")

    search_result = tavily_intense_search(
        query=search_prompt.content, search_category=search_category.content
    )

    thoughts["knowledge"] += search_result["results"]
    thoughts["shortterm_knowledge"] = search_result["results"]

    print()
    print(
        f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: knowledge - {search_category} [START] 🧠 - - - - - - -\n{json.dumps(thoughts['knowledge'], indent=4)}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: knowledge - {search_category} [END] 🧠 - - - - - - -"
    )
    print()
    # print(f"AGENT: shortterm_knowledge ==> {thoughts['shortterm_knowledge']}")
    return thoughts


def summarize(thoughts: AIBrain) -> AIBrain:
    """RISK ASSESSMENT NODE

    Parameters
    ----------
    thoughts : AIBrain
        state of LangGraph Agent

    Returns
    -------
    AIBrain
        state of LangGraph Agent
    """
    # Get relevant chunks from data
    doc_context = thoughts.get("data", {}).get("doc_context")
    survey_context = thoughts.get("data", {}).get("survey_context")

    # Add survey context if available
    if survey_context:
        chunk_context = f"[PATIENT PROFILE]\n{survey_context}\n\n[RELEVANT DOCUMENTS]\n{doc_context}"

    # Add survey context if available
    if survey_context:
        chunk_context = f"[PATIENT PROFILE]\n{survey_context['content']}\n\n[RELEVANT DOCUMENTS]\n{doc_context}"

    ## APPENDING RESEARCH RESULT INTO PROMPT
    if thoughts["knowledge"] == [] and not chunk_context:
        print(f"🧠 no knowledge is included")
        prompt = thoughts["prompt_chain"] + [
            {
                "role": "user",
                "content": (
                    "**MUST EXPLAIN EVERYTHING IN GENERALIZED PHRASES**, like 'people with [user's health context] are also struggling with [your proposed conclusion]' or similar"
                    "Respond in sections: an explanation of what this means in context, what user should look out for (symptoms, potential diagnosis, next steps, if any), and side notes (if any)."
                ),
            }
        ]
    else:
        if not chunk_context:
            chunk_context = ""
        # Combine external knowledge with document chunks
        knowledge_context = (
            "\n\n".join(
                [
                    search_["content"] + " Title: " + search_["title"]
                    for search_ in thoughts["knowledge"]
                ]
            )
            if thoughts["knowledge"]
            else ""
        )

        prompt = thoughts["prompt_chain"] + [
            {
                "role": "user",
                "content": (
                    "Based on the information I provided, please summarize the key points and provide "
                    "any relevant insights or recommendations. "
                    "Reference the information here:\n\n"
                    + (
                        f"[BEGIN OF DOCUMENT CHUNKS]\n{chunk_context}\n[END OF DOCUMENT CHUNKS]\n\n"
                        if chunk_context
                        else ""
                    )
                    + (
                        f"[BEGIN OF KNOWLEDGE]\n{knowledge_context}\n[END OF KNOWLEDGE]\n\n"
                        if knowledge_context
                        else ""
                    )
                    + "Summarize the information and use phrases like 'according to [insert source title]' to indicate the source of the information. "
                    "**MUST EXPLAIN EVERYTHING IN GENERALIZED PHRASES**, like 'people with [user's health context] are also struggling with [your proposed conclusion]' or similar"
                    "Respond in sections: an explanation of what this means in context, what user should look out for (symptoms, potential diagnosis, next steps, if any), and side notes (if any)."
                ),
            }
        ]

    print()
    print(
        f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [START] 🧠 - - - - - - -\n{json.dumps(prompt, indent=4)}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [END] 🧠 - - - - - - -"
    )
    print()

    ## COUNTING THE NUMBER OF TOKENS FOR LOGGING
    token_count = (
        len(" ".join([pt["content"] for pt in prompt]).split(" ")) / 1500.0
    ) * 2048

    print(f" 🧠 ===OPENAI=== Token Count Estimate: {token_count} 🧠 ")

    ## GET AI RESPONSE
    final_response = get_llm().invoke(prompt)

    prompt_chain_ai_obj = {
        "role": "assistant",
        "content": final_response.content,
        "references": thoughts["shortterm_knowledge"],
        "data": thoughts["data"]
    }

    ## adding the response to the chain too
    thoughts["prompt_chain"].append(prompt_chain_ai_obj)
    return thoughts


def initializeGraph(with_state: bool = True, prompt_chain: list = []):
    """Initialize the LangGraph state

    Parameters
    ----------
    with_state : bool, optional
        indicating the use of custom state or default empty state (refer to langgraph_obj.py AIBrain class), by default True
    prompt_chain : list, optional
        chain of messages to be initialized with, by default []

    Returns
    -------
    CompiledStateGraph
        the state of LangGraph, one for each chat / thread
    """

    # init_state = AIBrain(
    #     prompt_chain=[{
    #             "role": "system",
    #             "content": (
    #                 "You are a medical assistant, but not a licensed medical professional. "
    #                 "You will provide insights based on the information and any patient data you have gathered. "
    #                 "You will not provide any explicit medical advice or diagnosis, but you can talk about the generic knowledge related to the prompt. " ## NEED FURTHER TUNING
    #             )
    #         }],
    #     data={},
    #     risk_level=0,
    #     knowledge=[],
    #     category_focus=None
    # )

    memory = MemorySaver()
    # print(f"Initializing with user {user_id}")
    
    if with_state:
        state = AIBrain(
            thread_id="",
            user_id=user_id, ## only needed when with_state is True
            prompt_chain=(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a medical assistant, but not a licensed medical professional. "
                            "You will provide insights but not direct diagnosis, based on the information and any patient data you have gathered. "
                            "You will ask question about users' condition if you need more information for judgements. You always ask more questions if you need more information. "
                            "You will response in the format of suspected condition, next steps, and disclaimers that clarify you are not diagnosing."
                        ),
                    }
                ]
                if prompt_chain == []
                else prompt_chain
            ),
            data={
                "survey_context": "",
                "doc_context": ""
                },
            risk_level=0,
            knowledge=[],
            relevance=0,
            data_extraction_completed=False,
            proceed=False,
            shortterm_knowledge=[],
            category_focus=None,
        )

    workflow = StateGraph(AIBrain)

    # workflow.add_node("risk_assessment")
    workflow.add_node("determine_relevance", determine_relevance)
    workflow.add_node("refocus_medicine", refocus_medicine)
    workflow.add_node("summarize", summarize)
    
    workflow.add_node("enough_info_dec_pt", enough_info_dec_pt) ## simply evaluate if it has enough information
    workflow.add_node("enough_info_dec_pt_post_extract", enough_info_dec_pt_post_extract) ## evaluate if it has enough information AFTER DATA EXTRACTION
    
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("knowledge_gathering", knowledge_gathering)
    workflow.add_node("respond_manner", respond_manner)
    workflow.add_node("data_extract", data_extract)

    def enough_user_provided_info_conditional(thoughts: AIBrain) -> str:
        """Decision Point for determining if user provided enough information to proceed with the next steps."""
        if not thoughts["proceed"]:
            return "data_extract" ## Scrape from what we have
        else:
            return "knowledge_gathering" ## Enrich knowledge
        
    def enough_scraped_info_conditional(thoughts: AIBrain) -> str:
        """Decision Point for determining if scraped information provided enough information to proceed with next steps."""
        if not thoughts["proceed"]:
            return "generate_question" ## Nothing we could find, ask question
        else:
            return "knowledge_gathering" ## Enrich knowledge


    def discussion_relevance_conditional(thoughts: AIBrain) -> str:
        """Decision Point for determining if the discussion is relevant to medicine."""
        if thoughts["relevance"] == -1.0:
            return "respond_manner"  # Handle greetings or thank you messages
        elif thoughts["relevance"] < 0.5:
            return "refocus_medicine"
        else:
            return "enough_info_dec_pt"  # Proceed to check for enough information


    workflow.add_edge(START, "determine_relevance")
    
    
    workflow.add_conditional_edges(
        "enough_info_dec_pt",
        enough_user_provided_info_conditional,
        [
            "data_extract",
            "knowledge_gathering"
        ]
    )
    
    workflow.add_conditional_edges(
        "enough_info_dec_pt_post_extract",
        enough_scraped_info_conditional,
        [
            "generate_question",
            "knowledge_gathering"
        ]
    )
    
    workflow.add_edge("data_extract", "enough_info_dec_pt_post_extract")
    workflow.add_edge("knowledge_gathering", "summarize")
    workflow.add_conditional_edges(
        "determine_relevance",
        discussion_relevance_conditional,
        [
            "refocus_medicine",
            "enough_info_dec_pt",
            "respond_manner",
        ],
    )

    # workflow.set_entry_point("summarize")

    app = workflow.compile(checkpointer=memory)
    if with_state:
        # print(f"Initialized with state ==> {state}")
        return app, state
    else:
        return app


def trigger_response(graph, user_state: AIBrain) -> AIBrain:

    config = {"configurable": {"thread_id": user_state["thread_id"]}}
    state = graph.get_state(config)
    # print(f"Current state: {state}")
    response = graph.invoke(user_state, config)
    return response
