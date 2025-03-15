import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

from langchain_openai import ChatOpenAI
from constants.credentials import OPENAI_API_KEY

from langgraph.graph import START, StateGraph, END

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel
from typing import TypedDict, List, Dict



class AIBrain(TypedDict):
    thread_id: str ## thread id for the current conversation
    prompt_chain: List[Dict[str, str]] = [{
                "role": "system",
                "content": (
                    "You are a medical assistant, but not a licensed medical professional. "
                    "You will provide insights based on the information and any patient data you have gathered. "
                    "You will ask question about users' condition if you need more information for judgements."
                    "You will response in the format of suspected condition, next steps, and disclaimers that clarify you are not diagnosing."
                    # "You will not provide any explicit medical advice or diagnosis, but you can talk about the generic knowledge related to the prompt. " ## NEED FURTHER TUNING
                )
            }] ## list of prompt chain
    
    ## Personal Data
    data: Dict[str, Dict] ## user data
    
    ## Safety Parameter 
    risk_level: int ## 1 to 10 risk level 
    
    ## Knowledge Parameter
    knowledge: List[Dict] ## tavily search result [full list]
    ## sample: 
    #     "results": [
    #     {
    #       "title": "Dysbiosis: What is It and How to Heal Your Microbiome",
    #       "url": "https://drjockers.com/dysbiosis/",
    #       "content": "Dysbiosis is a condition where the gut microbiome is out of balance. Learn the major causes and support strategies to heal dysbiosis.",
    #       "score": 0.8790744,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: Causes, treatments, and more - Medical News Today",
    #       "url": "https://www.medicalnewstoday.com/articles/dysbiosis",
    #       "content": "Dysbiosis is when there is an issue with the diversity of someone's gut bacteria. Understand more about the causes and treatments for this condition.",
    #       "score": 0.85995835,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: What Is It, Causes, and More | Osmosis",
    #       "url": "https://www.osmosis.org/answers/dysbiosis",
    #       "content": "Dysbiosis is commonly linked to impaired gut barrier function and immune-mediated inflammation, which is a result of an excessive immune response. Therefore, there has been a potential association between intestinal dysbiosis and certain conditions, including inflammatory bowel disease (IBD), diabetes mellitus, and colorectal cancer.",
    #       "score": 0.8127637,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Gut Dysbiosis: Symptoms, Causes, Treatment and More - Health",
    #       "url": "https://www.health.com/gut-dysbiosis-8601756",
    #       "content": "Gut dysbiosis is an imbalance of gut microorganisms—like bacteria, fungi, and protozoa—in your intestines. A balanced gut flora (microbiome) supports functions like digestion and immune response.",
    #       "score": 0.76321954,
    #       "raw_content": null
    #     },
    #     {
    #       "title": "Dysbiosis: Symptoms and How To Treat It - Verywell Health",
    #       "url": "https://www.verywellhealth.com/what-is-intestinal-dysbiosis-1945045",
    #       "content": "Intestinal dysbiosis is a condition where the gut flora is imbalanced. Learn how gut dysbiosis can play a role in a variety of health problems.",
    #       "score": 0.7253574,
    #       "raw_content": null
    #     }
    #   ]
    
    category_focus: str | None ## category focus for the current conversation, will be changed into a ENUM in future sprints || None: general information, no focus
    

def get_llm():
    """Return the LLM."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY,
        max_retries=3,
    )

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

def print_prompt_chain(thoughts: AIBrain) -> AIBrain:
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
    for i in AIBrain["prompt_chain"]:
        print(i["role"], i["content"])
    return thoughts

## IMPORTANT: this data extraction is conditional, depending on what is in "data" and what the user is asking
## there is also foundational data needed, so another separate logic is to find out which foundational data 
##                                              is missing then call api to extract them
## if foundational data could not be retrieved, the status should also be noted in the data field, indicating 
##                                              LLM tried to retrieve but failed
def data_extract(thoughts: AIBrain) -> AIBrain:
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
    thoughts["data"] = {}
    return thoughts

def information_gathering(thoughts: AIBrain) -> AIBrain:
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
    thoughts["knowledge"] = [] ## PLACEHOLDER FOR NOW, WILL BE UPDATED IN FUTURE SPRINTS
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
    
    final_response = get_llm().invoke(thoughts["prompt_chain"])
    ## TODO: APPEND RESPONSE TO PROMPT CHAIN
    
    
    ## adding the response to the chain too
    thoughts["prompt_chain"].append({"role": "assistant", "content": final_response.content})
    return thoughts
    
    

def initializeGraph(with_state: bool = True):
    
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
                    "You will provide insights based on the information and any patient data you have gathered. "
                    "You will ask question about users' condition if you need more information for judgements."
                    "You will response in the format of suspected condition, next steps, and disclaimers that clarify you are not diagnosing."
                )
            }],
            data={},
            risk_level=0,
            knowledge=[],
            category_focus=None
        )
    
    workflow = StateGraph(AIBrain)
    
    # workflow.add_node("risk_assessment")
    # workflow.add_node("print_prompt_chain")
    # workflow.add_node("data_extract")
    # workflow.add_node("information_gathering")
    workflow.add_node("summarize", summarize)
    workflow.add_edge(START, "summarize")
    
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
    print(f"Current state: {state}")
    response = graph.invoke(user_state, config)
    return response