# 
#
# AI Response Tagging
# ----
# References:
            # {
            #   "response": "The mitochondria is the powerhouse of the cell and plays a role in cellular respiration.",
            #   "references": [
            #       {
            #           "phrase": "powerhouse of the cell",
            #           "start": 24,
            #           "end": 46,
            #           "reference": {
            #               "source": "Wikipedia",
            #               "url": "https://en.wikipedia.org/wiki/Mitochondr,
            #               "explanation": "The mitochondria is the powerhouse of the cell.",
            #               "date": "2022-10-10"
            #          }    
            #       }
            #   ]
            # }
#
# Dictionary:
            # {
            #   "response": "The mitochondria is the powerhouse of the cell and plays a role in cellular respiration.",
            #   "annotations": [
            #       {
            #           "phrase": "mitochondria",
            #           "start": 4,
            #           "end": 16,
            #           "explanation": "An organelle in cells that generates energy."
            #       },
            #       {
            #           "phrase": "cellular respiration",
            #           "start": 64,
            #           "end": 84,
            #           "explanation": "The process by which cells convert nutrients into energy."
            #       }
            #   ]
            # }
#
#
#


import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

import json
from langchain_openai import ChatOpenAI
from constants.credentials import OPENAI_API_KEY
from constants.langgraph_obj import (
    AIBrain
)

from dependencies.tavily_dependencies import (
    tavily_intense_search,
)

from langgraph.graph import START, StateGraph, END

# from langchain_core.messages import (
#     BaseMessage,
#     HumanMessage,
#     ToolMessage,
# )
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver


def get_llm():
    """Return the LLM."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY,
        max_retries=3,
    )
    
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
    
    session_history = thoughts["prompt_chain"]
        
    reconstructed_prompt = session_history + [{
        "role": "user",
        "content": ("Is the last message relevant to health? "
                    "Only answer strictly as a decimal value ranging 0 to 1."
                    "0 means not relevant at all, and 1 means very relevant."
                    "Consider the context of the conversation and the user's intent."
                    "Phatic expression, like 'hi', 'sorry', 'thank you', 'how are you', has to be given -1, but as only edge case.")
    }]
    
    decision = get_llm().invoke(reconstructed_prompt)
    
    print(f"🧠 AGENT: DECISION POINT - Relevance score: {decision.content} 🧠")
    
    thoughts["relevance"] = float(decision.content)
    
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
    
    print(f"🧠 AGENT: DECISION POINT - Responding to polite message 🧠")
    
    tmp_prompt = thoughts["prompt_chain"] + [{
        "role": "user",
        "content": ("Ask me what I need, but consider the context and health focus.")
    }]
    
    ai_question = get_llm().invoke(tmp_prompt)
    
    thoughts["prompt_chain"].append({
        "role": "assistant",
        "content": ai_question.content,
        "references": thoughts.get("shortterm_knowledge", [])
    })
    
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
    thoughts["prompt_chain"].append({
        "role": "assistant",
        "content": "Let's circle back to health discussion. What specific health-related question do you have?",
        "references": []
    })
    
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
    
    session_history =  thoughts["prompt_chain"]
    user_messages = [message_obj for message_obj in session_history if message_obj["role"] == "user"]
    sringified_user_messages = "\n".join([message_obj["content"] for message_obj in user_messages])
        
    reconstructed_prompt = [{
        "role": "user",
        "content": (sringified_user_messages + "\n" +
                    "Is there enough information to proceed with the next steps? "
                    "Only answer strictly (without punctuation or space) 'yes' or 'no'. ")
    }]
    
    decision = get_llm().invoke(reconstructed_prompt)
    
    if decision.content == "yes":
        print("🧠 AGENT: DECISION POINT - Proceeding with the next steps 🧠")
        thoughts["proceed"] = True
    elif decision.content == "no":
        print("🧠 AGENT: DECISION POINT - Not enough information to proceed 🧠")
        thoughts["proceed"] = False
    else:
        print("🧠 AGENT: DECISION POINT - Invalid response. Defaulting to not proceed. Value: ", decision.content, " 🧠")
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
    
    tmp_prompt = thoughts["prompt_chain"] + [{
        "role": "user",
        "content": ("What other details do you need from me? Give me one question.")
    }]
    
    ai_question = get_llm().invoke(tmp_prompt)
    
    thoughts["prompt_chain"].append({
        "role": "assistant",
        "content": ai_question.content,
        "references": thoughts.get("shortterm_knowledge", [])
    })
    
    return thoughts


def assess_risk(thoughts: AIBrain) -> AIBrain:
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
    thoughts["risk_level"] = 0 ## PLACEHOLDER FOR NOW, WILL BE UPDATED IN FUTURE SPRINTS
    
    
    ## TODO: CHECK IF PROMPT PASSES RISK ASSESSMENT
    ## IF YES, APPEND RESPONSE TO PROMPT CHAIN
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
    thoughts["data"] = {}
    return thoughts

def information_gathering(thoughts: AIBrain) -> AIBrain:
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
    
    search_prompt = get_llm().invoke(thoughts["prompt_chain"] + [{
        "role": "user",
        "content": ("Summarize the key points into a search query with a maximum of 400 characters. "
                    "This query will be used to search for relevant information on the internet.")
    }])
    
    search_category = get_llm().invoke(thoughts["prompt_chain"] + [{
        "role": "user",
        "content": ("Determine the category of the search query. "
                    "Strictly respond with one of the following categories: 'diagnosis', 'next_steps', 'research_papers'.")
    }])
    
    # print(f"AGENT: search metadata => {search_prompt.content}, {search_category.content}")
    
    search_result = tavily_intense_search(query=search_prompt.content, search_category=search_category.content)    
    
    thoughts["knowledge"] += search_result["results"]
    thoughts["shortterm_knowledge"] = search_result["results"] 
    
    print()
    print(f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: knowledge - {search_category} [START] 🧠 - - - - - - -\n{json.dumps(thoughts['knowledge'], indent=4)}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: knowledge - {search_category} [END] 🧠 - - - - - - -")
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
    
    ## APPENDING RESEARCH RESULT INTO PROMPT
    if thoughts["knowledge"] == []:
        print(f"🧠 no knowledge is included")
        prompt =  thoughts["prompt_chain"] + [{
            "role": "user",
            "content": (
                "Based on the information I provided, please summarize the key points and provide "
                "any relevant insights or recommendations. "
                "Please respond in sections: risk level (high, medium, low), suspected condition, next steps, and any disclaimers"
                "that you are not an official medical diagnosis."
            )
        }]
    else:
        prompt = thoughts["prompt_chain"] + [{
            "role": "user",
            "content": (
                "Based on the information I provided, please summarize the key points and provide "
                "any relevant insights or recommendations. "
                "Reference the information here: [BEGIN OF KNOWLEDGE] " + "\n\n".join([search_["content"] + " Title: " + search_["title"] for search_ in thoughts["knowledge"]]) + ". [END OF KNOWLEDGE]\n\n"
                # "Please exclusively check which information is relevant to the user's condition and summarize them, with clear indication 'according to [insert source title]'. "
                "Summarize the information and use phrases like 'according to [insert source title]' to indicate the source of the information. "
                "Respond in sections: risk level (high, medium, low), suspected condition, next steps, and side notes (if any)."
            )
        }]
        
    print()
    print(f"- - - - - - - 🧠 [START] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [START] 🧠 - - - - - - -\n{json.dumps(prompt, indent=4)}\n- - - - - - - 🧠 [END] AGENT {thoughts['thread_id']}: 'Summarize' Prompt [END] 🧠 - - - - - - -")
    print()
        
    ## COUNTING THE NUMBER OF TOKENS FOR LOGGING
    token_count = (len(' '.join([pt["content"] for pt in prompt]).split(" "))  / 1500.0) * 2048
    
    print(f" 🧠 ===OpenAI=== Token Count Estimate: {token_count} 🧠 ")
    
    ## GET AI RESPONSE
    final_response = get_llm().invoke(prompt)
    
    prompt_chain_ai_obj = {
        "role": "assistant",
        "content": final_response.content,
        "references": thoughts["shortterm_knowledge"]
    }
    
    ## adding the response to the chain too
    thoughts["prompt_chain"].append(prompt_chain_ai_obj)
    return thoughts
    
    

def initializeGraph(with_state: bool = True, prompt_chain: list =[]):
    
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
    if with_state:
        state = AIBrain(
            thread_id="",
            prompt_chain=[{
                "role": "system",
                "content": (
                    "You are a medical assistant, but not a licensed medical professional. "
                    "You will provide insights but not direct diagnosis, based on the information and any patient data you have gathered. "
                    # "You will ask question about users' condition if you need more information for judgements, but keep them one at a time."
                    # "When a conclusion is reached, you will respond in the format of suspected condition, next steps, and disclaimers that clarify you are not diagnosing."
                )
            }] if prompt_chain == [] else prompt_chain,
            data={},
            risk_level=0,
            knowledge=[],
            relevance=0,
            proceed=False,
            shortterm_knowledge=[],
            category_focus=None
        )
    
    workflow = StateGraph(AIBrain)
    
    # workflow.add_node("risk_assessment")
    # workflow.add_node("data_extract")
    # workflow.add_node("information_gathering")
    workflow.add_node("determine_relevance", determine_relevance)
    workflow.add_node("refocus_medicine", refocus_medicine)
    workflow.add_node("summarize", summarize)
    workflow.add_node("enough_info_dec_pt", enough_info_dec_pt)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("information_gathering", information_gathering)
    workflow.add_node("respond_manner", respond_manner)
    
    def enough_information_conditional(thoughts: AIBrain) -> str:
        """Decision Point for determining if there is enough information to proceed with the next steps."""
        return "generate_question" if not thoughts["proceed"] else "information_gathering"
    
    def discussion_relevance_conditional(thoughts: AIBrain) -> str:
        """Decision Point for determining if the discussion is relevant to medicine."""
        if thoughts["relevance"] == -1.0:
            return "respond_manner"  # Handle greetings or thank you messages
        elif thoughts["relevance"] < 0.5: 
            return "refocus_medicine"
        else:
            return "enough_info_dec_pt"  # Proceed to check for enough information
    
    workflow.add_edge(START, "determine_relevance")  # Start with the relevance check
    workflow.add_conditional_edges(
        "enough_info_dec_pt",
        enough_information_conditional,
        ["generate_question", "information_gathering"]  # if enough info, go to summarize, else generate question
    )
    workflow.add_edge("information_gathering", "summarize")  # After gathering info, go to summarize
    workflow.add_conditional_edges(
        "determine_relevance",
        discussion_relevance_conditional,
        ["refocus_medicine", "enough_info_dec_pt", "respond_manner"]  # if not relevant, refocus, else check for enough info
    )
    
    # workflow.set_entry_point("summarize")
    
    app = workflow.compile(checkpointer=memory)
    if with_state:
        print(f"Initialized with state ==> {state}")
        return app, state
    else:
        return app

def trigger_response(graph, user_state: AIBrain) -> AIBrain:
    
    config = {"configurable": {"thread_id": user_state["thread_id"]}}
    state = graph.get_state(config)
    # print(f"Current state: {state}")
    response = graph.invoke(user_state, config)
    return response