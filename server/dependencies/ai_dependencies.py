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

from routers.whoop_connect import (
    whoop_access_token
)


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


def determine_relevance(thoughts: AIBrain) -> AIBrain:
    """RELEVANCE DECISION NODE
    Determines how relevant the user's message is to health-related topics, using a float score.

    Parameters
    ----------
    thoughts : AIBrain
        LangGraph Agent state.

    Returns
    -------
    AIBrain
        Updated state with `relevance` score and `health_mode` toggle.
    """

    thoughts["data_extraction_completed"] = False
    session_history = thoughts.get("prompt_chain", [])

    # Get the last user message for focused evaluation
    last_user_msg = next((m["content"] for m in reversed(session_history) if m["role"] == "user"), "")

    evaluation_prompt = session_history + [
        {
            "role": "system",
            "content": (
                "You are a relevance-scoring assistant. Your task is to evaluate how related the last user message is to health topics.\n"
                "\n"
                "Scoring Rules:\n"
                "1. If the latest message is **explicitly about health**, return a score between 0.5 and 1.\n"
                "2. If it is **not health-related but logically follows a prior health conversation**, return 0.3–0.6.\n"
                "3. If it is **completely unrelated to health**, return a score between 0 and 0.3.\n"
                "4. If it is a polite or phatic message like 'thanks', 'okay', 'hi', etc., return -1.\n"
                "\n"
                "Examples:\n"
                "'I feel dizzy in the morning' → 0.8\n"
                "'Thanks, bye!' → -1\n"
                "'What’s your favorite movie?' → 0.1\n"
                "\n"
                f"Evaluate this message: \"{last_user_msg}\"\n"
                "\nReturn **only** the decimal score (no explanation)."
            )
        }
    ]

    decision = get_llm().invoke(evaluation_prompt)

    try:
        relevance_score = float(decision.content.strip())
    except ValueError:
        relevance_score = 0.0  # fallback safety

    thoughts["relevance"] = relevance_score

    # Toggle health mode
    if relevance_score >= 0.5:
        thoughts["health_mode"] = True
    elif relevance_score < 0.3:
        thoughts["health_mode"] = False

    return thoughts



def respond_manner(thoughts: AIBrain) -> AIBrain:
    """Gracefully handle polite messages with context-aware redirection."""

    # Extract last user message
    last_user_msg = ""
    for msg in reversed(thoughts["prompt_chain"]):
        if msg["role"] == "user":
            last_user_msg = msg["content"].lower()
            break

    # Basic keyword logic for tailoring response type
    if any(greet in last_user_msg for greet in ["hi", "hello", "good morning", "hey"]):
        tone = "greeting"
    elif any(bye in last_user_msg for bye in ["thank", "bye", "see you", "take care"]):
        tone = "farewell"
    else:
        tone = "generic"

    # Construct contextual system prompt
    system_prompt = {
        "role": "system",
        "content": (
            "You are a friendly, helpful assistant. If the user greeted you, greet them warmly and ask what health concern they’d like to discuss. "
            "If they thanked you or ended the conversation, respond kindly and let them know you’re here if they need anything else. "
            "Keep it natural, short, and respectful."
        )
    }

    user_prompt = {
        "role": "user",
        "content": f"The user just said: \"{last_user_msg}\". Respond appropriately."
    }

    ai_response = get_llm().invoke([system_prompt, user_prompt])

    thoughts["prompt_chain"].append(
        {
            "role": "assistant",
            "content": ai_response.content,
            "references": thoughts.get("shortterm_knowledge", []),
        }
    )

    return thoughts


def refocus_medicine(thoughts: AIBrain) -> AIBrain:
    """REFOCUS NODE
    Prompts the user to steer the conversation back toward a medically relevant topic.

    Parameters
    ----------
    thoughts : AIBrain
        State of the LangGraph Agent.

    Returns
    -------
    AIBrain
        Updated agent state.
    """

    refocus_prompt = {
        "role": "assistant",
        "content": (
            "Let's circle back to health. What specific health-related question or concern would you like to explore?"
        ),
        "references": [],
    }

    thoughts["prompt_chain"].append(refocus_prompt)
    return thoughts

def enough_info_dec_pt(thoughts: AIBrain) -> AIBrain:
    """Early Decision Node: Check if user input and dialogue are sufficient to proceed."""

    prompt_chain = thoughts.get("prompt_chain", [])

    def extract_recent_dialogue(chain, max_pairs=3):
        assistant_msgs = [m["content"] for m in chain if m["role"] == "assistant" and "?" in m["content"]][-max_pairs:]
        user_msgs = [m["content"] for m in chain if m["role"] == "user" and len(m["content"].split()) > 5][-max_pairs:]
        dialogue = []
        for a, u in zip(assistant_msgs, user_msgs):
            dialogue.append(f"Assistant: {a}\nUser: {u}")
        return "\n\n".join(dialogue)

    conversation_context = extract_recent_dialogue(prompt_chain)

    decision_prompt = [
        {
            "role": "system",
            "content": (
                "You are a reasoning agent tasked with determining if there is enough context to begin medical summarization.\n"
                "You must consider both the assistant's clarifying questions and the user's replies.\n"
                "Reply with one word only: 'yes' or 'no'."
            )
        },
        {
            "role": "user",
            "content": (
                f"Conversation So Far:\n\n{conversation_context or 'None'}\n\n"
                "Is there enough detail to proceed with a medically-informed answer?"
            )
        }
    ]

    decision = get_llm().invoke(decision_prompt)
    normalized = decision.content.strip().lower()
    thoughts["proceed"] = normalized == "yes"


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

    prompt_chain = thoughts.get("prompt_chain", [])
    survey_data = thoughts["data"].get("survey_context", "")
    doc_data = thoughts["data"].get("doc_context", "")

    # --- Collect informative user messages (skip 'yes', 'okay', etc.) ---
    def extract_useful_user_messages(chain, min_words=6, max_messages=12):
        return [
            m["content"] for m in chain
            if m["role"] == "user" and len(m["content"].split()) >= min_words
        ][-max_messages:]

    # --- Optionally include last assistant clarification question ---
    def extract_relevant_ai_prompt(chain):
        for m in reversed(chain):
            if m["role"] == "assistant" and "?" in m["content"]:
                return m["content"]
        return ""

    filtered_user_msgs = extract_useful_user_messages(prompt_chain)
    last_ai_prompt = extract_relevant_ai_prompt(prompt_chain)

    user_text = "\n".join(filtered_user_msgs)

    # --- Build prompt ---
    decision_prompt = [
        {
            "role": "system",
            "content": (
                "You are a reasoning assistant that decides whether there is enough information to provide a helpful, medically grounded insight.\n"
                "Only respond with one word: 'yes' or 'no'. No explanations."
            )
        },
        {
            "role": "user",
            "content": (
                f"Patient Profile:\n{survey_data or 'None'}\n\n"
                f"Document Context:\n{doc_data or 'None'}\n\n"
                f"Assistant Prompt:\n{last_ai_prompt or 'None'}\n\n"
                f"User Responses:\n{user_text or 'None'}\n\n"
                "Is this enough to proceed with health insight?"
            )
        }
    ]

    # --- Evaluate LLM output ---
    decision = get_llm().invoke(decision_prompt)
    normalized = decision.content.strip().lower()
    thoughts["proceed"] = normalized == "yes"

    return thoughts

def enough_info_dec_pt_post_extract(thoughts: AIBrain) -> AIBrain:
    """Decision Point: Assess if enough medical context has been gathered to proceed.
    Uses patient profile, document context, and conversational history.
    """

    prompt_chain = thoughts.get("prompt_chain", [])
    survey_data = thoughts["data"].get("survey_context", "")
    doc_data = thoughts["data"].get("doc_context", "")


    # --- Collect informative user messages (skip 'yes', 'okay', etc.) ---
    def extract_useful_user_messages(chain, min_words=6, max_messages=12):
        return [
            m["content"] for m in chain
            if m["role"] == "user" and len(m["content"].split()) >= min_words
        ][-max_messages:]

    # --- Optionally include last assistant clarification question ---
    def extract_relevant_ai_prompt(chain):
        for m in reversed(chain):
            if m["role"] == "assistant" and "?" in m["content"]:
                return m["content"]
        return ""

    filtered_user_msgs = extract_useful_user_messages(prompt_chain)
    last_ai_prompt = extract_relevant_ai_prompt(prompt_chain)

    user_text = "\n".join(filtered_user_msgs)

    # --- Build prompt ---
    decision_prompt = [
        {
            "role": "system",
            "content": (
                "You are a reasoning assistant that decides whether there is enough information to provide a helpful, medically grounded insight.\n"
                "Only respond with one word: 'yes' or 'no'. No explanations."
            )
        },
        {
            "role": "user",
            "content": (
                f"Patient Profile:\n{survey_data or 'None'}\n\n"
                f"Document Context:\n{doc_data or 'None'}\n\n"
                f"Assistant Prompt:\n{last_ai_prompt or 'None'}\n\n"
                f"User Responses:\n{user_text or 'None'}\n\n"
                "Is this enough to proceed with health insight?"
            )
        }
    ]

    # --- Evaluate LLM output ---
    decision = get_llm().invoke(decision_prompt)
    normalized = decision.content.strip().lower()
    thoughts["proceed"] = normalized == "yes"

    return thoughts


def generate_question(thoughts: AIBrain) -> AIBrain:
    """QUESTION GENERATION NODE
    ---------------------------
    Generates clarifying or follow-up questions when not enough information is present.
    """
    
    survey_data = thoughts["data"].get("survey_context", "")
    doc_data = thoughts["data"].get("doc_context", "")
    prompt_chain = thoughts["prompt_chain"]
    
    # Ensure profile context is present in system prompt
    if "Patient Profile:" not in prompt_chain[0].get("content", ""):
        prompt_chain[0]["content"] += (
            "\n\nYou must consider the patient’s profile and history in all your reasoning.\n"
            f"Patient Profile:\n{survey_data or 'None'}"
        )
        
    # Add user message context for document content
    tmp_prompt = prompt_chain + [
        {
            "role": "user",
            "content": (
                "Below are relevant medical documents or notes for this user:\n\n"
                f"{doc_data or 'None'}\n\n"
                "Please use this context to guide your follow-up."
            )
        },
        {
            "role": "user",
            "content": (
                "If the user's last message was a quick clarification question "
                "(e.g., 'Is that bad?', 'Should I avoid this?'), respond to it briefly "
                "**first** (1–2 clear sentences).\n\n"
                "Then, ask 1–3 simple follow-up questions to better understand their condition.\n"
                "The questions should be short, friendly, and easy to understand.\n"
                "**Highlight** the questions in bold, but do not number or bullet-point them."
            )
        }
    ]
    
    # Debug logging
    print()
    print(
        f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: 'Generate Question' Prompt [START] 🧠 - - - - - - -\n"
        f"{json.dumps(tmp_prompt, indent=4)}\n"
        f"- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: 'Generate Question' Prompt [END] 🧠 - - - - - - -"
    )
    print()

    # LLM call
    ai_question = get_llm().invoke(tmp_prompt)

    # Store assistant response
    thoughts["prompt_chain"].append({
        "role": "assistant",
        "content": ai_question.content,
        "references": thoughts.get("shortterm_knowledge", [])
    })

    return thoughts


## IMPORTANT: this data extraction is conditional, depending on what is in "data" and what the user is asking
## there is also foundational data needed, so another separate logic is to find out which foundational data
##                                              is missing then call api to extract them
## if foundational data could not be retrieved, the status should also be noted in the data field, indicating
##                                              LLM tried to retrieve but failed
def doc_data_extract(thoughts: AIBrain) -> AIBrain:
    """DATA EXTRACTION NODE
    ------------------------
    Searches internal systems (Firestore, ChromaDB) for the user's health data and stores relevant context in the agent's state.
    """
    
    user_id = thoughts.get("user_id")

    if not user_id:
        raise ValueError("🧠 User ID missing from thoughts.")
    
    # Retrieve profile data and convert into usable string context
    survey_data = get_profile(user_id=user_id)
    survey_context = get_survey_context(survey_data=survey_data)
    if survey_context:
        thoughts["data"]["survey_context"] = survey_context
    
    # Use latest user input to query document knowledge
    last_message = thoughts["prompt_chain"][-1].get("content", "")
    relevant_docs = query_docs_from_chroma(prompt=last_message, premise={"user_id": user_id})
    
    # Join flattened text chunks into a single context string
    doc_content = " ".join([doc[0] for doc in relevant_docs.get("documents", [])])
    if doc_content.strip():
        thoughts["data"]["doc_context"] = doc_content

    return thoughts

def whoop_data_extract(thoughts: AIBrain) -> AIBrain:
    """WHOOP DATA EXTRACTION NODE"""



def knowledge_gathering(thoughts: AIBrain) -> AIBrain:
    """
    INFORMATION GATHERING NODE
    ---------------------------
    Uses the conversation history to generate a search query and category, then enriches the agent's short-term memory
    with Tavily-powered knowledge lookup.
    """

    thread_id = thoughts.get("thread_id", "UNKNOWN")
    prompt_chain = thoughts.get("prompt_chain", [])

    # Generate a concise search query from the conversation
    query_response = get_llm().invoke(
        prompt_chain + [
            {
                "role": "user",
                "content": (
                    "Summarize the key points into a search query with a maximum of 400 characters. "
                    "This query will be used to search for relevant information on the internet."
                )
            }
        ]
    )
    
    search_query = query_response.content.strip()
    if not search_query:
        print(f"❌ [thread {thread_id}] No search query generated.")
        return thoughts

    # Classify the category of the query
    category_response = get_llm().invoke(
        prompt_chain + [
            {
                "role": "user",
                "content": (
                    "Determine the category of the search query. "
                    "Strictly respond with one of the following categories: 'diagnosis', 'next_steps', 'research_papers'."
                )
            }
        ]
    )
    
    search_category = category_response.content.strip().lower()
    if search_category not in ["diagnosis", "next_steps", "research_papers"]:
        print(f"❌ [thread {thread_id}] Invalid search category: {search_category}")
        return thoughts

    print(f"🌐 [thread {thread_id}] Query: {search_query}")
    print(f"📂 [thread {thread_id}] Category: {search_category}")


    # print(f"AGENT: search metadata => {search_prompt.content}, {search_category.content}")

    # Perform external search
    try:
        search_result = tavily_intense_search(
            query=search_query, search_category=search_category
        )
    except Exception as e:
        print(f"❌ [thread {thread_id}] Tavily search failed: {e}")
        return thoughts

    results = search_result.get("results", [])


    # Save into thoughts
    thoughts["knowledge"] += results
    thoughts["shortterm_knowledge"] = results

    print(
        f"\n- - - - - - - 🧠 [START] AGENT {thread_id}: knowledge - {search_category} 🧠 - - - - - - -\n"
        f"{json.dumps(results, indent=4)}\n"
        f"- - - - - - - 🧠 [END] AGENT {thread_id}: knowledge - {search_category} 🧠 - - - - - - -\n"
    )

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
    
    # Get user context
    survey_data = thoughts["data"].get("survey_context", "")
    doc_data = thoughts["data"].get("doc_context", "")
    knowledge_data = thoughts.get("knowledge", [])
    chunk_context = thoughts["data"].get("chunk_context", "")

    # Append structured patient profile to the last user-facing instruction
    processed_prompt_chain = thoughts["prompt_chain"]
    processed_prompt_chain[0]["content"] += (
        "\n\nYou must consider the patient’s profile and history in all your reasoning.\n"
        f"Patient Profile:\n{survey_data or 'None'}"
    )

    # RAG + Doc context section
    knowledge_context = "\n\n".join(
        f"{k['content']} (Source: {k['title']})" for k in knowledge_data
    ) if knowledge_data else ""

    doc_context_block = f"[User's Medical Documents]\n{doc_data or 'None'}\n[End of User's Medical Documents]"
    knowledge_block = f"[BEGIN OF KNOWLEDGE]\n{knowledge_context}\n[END OF KNOWLEDGE]" if knowledge_context else ""

    if not knowledge_context and not chunk_context:
        print("🧠 No knowledge is included")
        user_instruction = (
            "**MUST EXPLAIN EVERYTHING IN GENERALIZED PHRASES**, like "
            "'people with [user's health context] are also struggling with [your proposed conclusion]' or similar.\n\n"
            "Respond in sections:\n"
            "1. Explanation of what this means in context\n"
            "2. What user should look out for (symptoms, potential diagnosis, next steps)\n"
            "3. Side notes (if any)"
        )
    else:
        user_instruction = (
            "Based on the information I provided, please summarize the key points and provide any relevant insights or recommendations.\n\n"
            f"{doc_context_block}\n\n"
            f"{knowledge_block}\n\n"
            "Summarize the information and use phrases like 'according to [insert source title]' to indicate the source of the information. "
            "**MUST EXPLAIN EVERYTHING IN GENERALIZED PHRASES SO YOU ARE NOT GIVING SPECIFIC MEDICAL DECISIONS**, like "
            "'people with [user's health context] are also struggling with [your proposed conclusion]' or similar.\n\n"
            "Respond in sections:\n"
            "1. Explanation of what this means in context\n"
            "2. What user should look out for (symptoms, potential diagnosis, next steps)\n"
            "3. Side notes (if any)"
            "You can highlight or bold phrases if they are keywords, like medical terminology."
        )

    # Append the new user instruction
    prompt = processed_prompt_chain + [{"role": "user", "content": user_instruction}]

    print()
    print(
        f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [START] 🧠 - - - - - - -\n"
        f"{json.dumps(prompt, indent=4)}\n"
        f"- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [END] 🧠 - - - - - - -"
    )
    print()

    # === TOKEN COUNT ESTIMATION ===
    token_count = (
        len(" ".join([pt["content"] for pt in prompt]).split()) / 1500.0
    ) * 2048
    print(f" 🧠 ===OPENAI=== Token Count Estimate: {token_count:.2f} 🧠 ")
    
    # === GET AI RESPONSE ===
    try:
        final_response = get_llm().invoke(prompt)
    except Exception as e:
        print(f"❌ Error invoking LLM in 'Summarize' node: {e}")
        raise

    # === FORMAT RESPONSE INTO CHAIN ===
    prompt_chain_ai_obj = {
        "role": "assistant",
        "content": final_response.content,
        "references": thoughts.get("shortterm_knowledge", []),
        "data": thoughts.get("data", {}),
    }

    thoughts["prompt_chain"].append(prompt_chain_ai_obj)

    return thoughts


def initializeGraph(with_state: bool = True, prompt_chain: list = [], user_id: str = ""):
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

    memory = MemorySaver()
    
    if with_state:
        # Initialize assistant prompt
        default_prompt = [
            {
                "role": "system",
                "content": (
                    "You are a kind, helpful health assistant. You are not a licensed medical professional and cannot give direct medical advice, but you can provide insights based on provided health records and user responses. "
                    "If you do not have enough information to give useful insight, you will ask the user 1–3 follow-up questions to gather it. Always write your questions in **simple, easy-to-understand language** suitable for someone without medical training. "
                    "You may highlight or bold the phrases (particularly questions or key terminology) for readability. "
                    "If the user’s last message contains a **quick clarification question** (e.g., “Does that mean it’s the milk?”, “Should I be worried about that?”), respond to that in 1–2 brief, clear sentences **first**, then continue asking follow-up questions afterward — all in the same message. "
                    "Do not repeat questions the user has already answered. Your goal is to keep the conversation helpful, informative, and easy to follow."
                ),
            }
        ]

        state = AIBrain(
            thread_id="",
            user_id=user_id,
            prompt_chain=prompt_chain if prompt_chain else default_prompt,
            data={"survey_context": "", "doc_context": ""},
            risk_level=0,
            knowledge=[],
            relevance=0,
            proceed=False,
            shortterm_knowledge=[],
            category_focus=None,
            needs_documents=False,
        )

    # Setup graph
    workflow = StateGraph(AIBrain)
    workflow.add_node("determine_relevance", determine_relevance)
    workflow.add_node("enough_info_dec_pt", enough_info_dec_pt)
    workflow.add_node("enough_info_dec_pt_post_extract", enough_info_dec_pt_post_extract)

    ## Response Nodes
    workflow.add_node("respond_manner", respond_manner)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("refocus_medicine", refocus_medicine)
    workflow.add_node("summarize", summarize)
    
    ## Knowledge Nodes
    workflow.add_node("knowledge_gathering", knowledge_gathering)
    
    ## Data Gathering Nodes
    workflow.add_node("doc_data_extract", doc_data_extract)
    
    
    

    # Conditional decision functions
    def enough_user_provided_info_conditional(thoughts: AIBrain) -> str:
        return "doc_data_extract" if not thoughts["proceed"] else "knowledge_gathering"

    def enough_scraped_info_conditional(thoughts: AIBrain) -> str:
        return "generate_question" if not thoughts["proceed"] else "knowledge_gathering"

    def discussion_relevance_conditional(thoughts: AIBrain) -> str:
        if thoughts["relevance"] == -1.0:
            return "respond_manner"
        elif thoughts["relevance"] < 0.5:
            return "refocus_medicine"
        return "enough_info_dec_pt"

    # Add workflow edges
    workflow.add_edge(START, "determine_relevance")
    workflow.add_edge("doc_data_extract", "enough_info_dec_pt_post_extract")
    workflow.add_edge("knowledge_gathering", "summarize")

    workflow.add_conditional_edges(
        "determine_relevance",
        discussion_relevance_conditional,
        ["refocus_medicine", "enough_info_dec_pt", "respond_manner"]
    )
    workflow.add_conditional_edges(
        "enough_info_dec_pt",
        enough_user_provided_info_conditional,
        ["doc_data_extract", "knowledge_gathering"]
    )
    workflow.add_conditional_edges(
        "enough_info_dec_pt_post_extract",
        enough_scraped_info_conditional,
        ["generate_question", "knowledge_gathering"]
    )

    app = workflow.compile(checkpointer=memory)
    return (app, state) if with_state else app


def trigger_response(graph, user_state: AIBrain) -> AIBrain:

    config = {"configurable": {"thread_id": user_state["thread_id"]}}
    state = graph.get_state(config)
    # print(f"Current state: {state}")
    response = graph.invoke(user_state, config)
    return response
