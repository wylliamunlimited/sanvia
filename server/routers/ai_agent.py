import sys

from openai import BaseModel

from dependencies.tavily_dependencies import get_tavily_client, tavily_search_function

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Dict
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_chat_entry,
    get_chat,
)
from constants.request_obj import (
    PromptRequest,
)
from constants.langgraph_obj import (
    AIBrain,
)
from dependencies.chat_dependencies import (
    create_new_thread
)
from dependencies.ai_dependencies import (
    get_llm,
    initializeGraph,
    trigger_response,
)
from langchain_core.messages import HumanMessage  # ✅ Correct Import
import random  ## TO BE REMOVED
from datetime import datetime
import json


router = APIRouter()


## recording the graph for each user
## NEEDED FOR ISOLATION OF USER CHAT & DATA
## Format:
# {
#     "user_id": AIBrain,
# }
states = {}


@router.get("/openai-health")
async def health_check():
    """
    Check the health of the OpenAI API.
    """
    try:
        response = get_llm().invoke([HumanMessage(content="Hello")])
        return {"openai_status": "Connected", "response": response.content}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"OpenAI connection issue: {str(e)}"
        )


## Chain of Prompts Example
# [
#     {
#         "role": "system",
#         "content": (
#             "You are a medical professional with rich medical knowledge and only answer medically relevant questions. "
#             "You will take the conversation step by step and not respond with a conclusion right after a prompt is enter. "
#             "Instead, you will ask user detailed clarification questions, one at a time, for further information, such as what user did "
#             "for the past few days or if they remember any minor accidents they had and might be related to their described conditions, if needed. "
#             "When you have sufficient information obtained by asking user clarification questions, you will answer with explanation, "
#             "such as cause and physiology of conditions, self-care options, how most people respond to the mentioned incoming problems or concerns, "
#             "and compare the conditions to other historical records of similar medical cases, if applicable. "
#             "If the incoming question is highly specific for an answer of a specific questions, you will solve the specific question first. \n\n"
#             "You also emphasize that your answer might not be perfect or applicable to everyone because of different physiological setup for every human. "
#             "You will provide disclaimer that your response is not a clinical diagnosis or recommendation of personalized treatment when you are answering "
#             "questions and have similar text in your answer. \n\n"
#             "Your summary response will be clearly segmented by coverage of topics, such as causes, common responses, resources, etc."
#         )
#     },
#     {
#         "role": "system",
#         "content": "Here are some premise data for user's health. The sugar metric of user is described in this data: " + sample_data + ". Use this data and compare if it is relevant to user's query. If it is, respond based on this data and reference it. If you want to visualize those data using bar graph, use '''<bar>[strictly the name of data source, such as 'sugar metric' in this case]|x-values separated by ','|y-values separated by ','<bar>'''"
#     },
#     {
#         "role": "assistant",
#         "content": "Hello! How can I help with your health related questions?"
#     }
# ]
# ]
@router.post("/ai-response")
async def ai_response(
    request: PromptRequest,
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    """[LEGACY] Obtain for AI Response

    Descriptions
    ------------
    - User authentication is required, token must be embedded in request header
    - Take in user prompt, and run LangGraph based on it
    - Update the LangGraph global states
    - If no prior chat for this user, it would create one for user

    Parameters
    ----------
    request : PromptRequest
        consist of a prompt

    Returns
    -------
    dict
        chat: str
            messages
        full_response: str
            ai response
        simple_response: str
            abstract ai response 
        total_sources: list[dict]
            all the references 
        sources: list[dict]
            references for ai response
        thread_id: str
            chat thread id

    Raises
    ------
    HTTPException 422
        indicate there is no prompt, parameter value is invalid
    HTTPException 
        general endpoint errors
    """

    if request is None or request.prompt is None:
        raise HTTPException(status_code=422, detail=f"Request does not contain prompt for AI to work with.")

    try:
        # Initialize user session if not active
        if user["uid"] not in states:
            thread_id = (
                user["uid"]
                + datetime.now().strftime("%Y%m%d%H%M%S")
                + str(random.randint(0, 1000))
            )
            _graph, _state = initializeGraph()
            _state["thread_id"] = thread_id
            states[user["uid"]] = _state
        else:
            _graph = initializeGraph(with_state=False)
            _state = states[user["uid"]]

        # Append user message to chat history
        _state["prompt_chain"].append({"role": "user", "content": request.prompt})
        states[user["uid"]] = _state

        # Call AI response
        response = trigger_response(_graph, _state)
        full_response = response["prompt_chain"][-1]["content"]  # Last AI response

        # Modify response based on complexity choice
        simple_response = (
            " ".join(full_response.split()[:30]) + "..."
        )  # Shortened summary

        # Save chat to Firestore
        update_chat_entry(
            user_id=user["uid"],
            thread_id=_state["thread_id"],
            chat_data={
                "prompt_chain": _state["prompt_chain"],
                "sources": _state["knowledge"],
                "last_updated_at": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            },
        )

        return {
            "chat": _state["prompt_chain"],
            "full_response": full_response,  # Full text for "See More"
            "simple_response": simple_response,  # Now correctly accessible
            "total_sources": _state.get("knowledge", []),  # All sources used in the chat
            "sources": _state.get("shortterm_knowledge", []),  # Tavily search results
            "thread_id": _state["thread_id"],
        }

    except Exception as e:
        print(f"AI Response Trigger Error: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.post("/destroy-chat-session")
async def destroy_chat_session(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    """[LEGACY ENDPOINT] Remove session from active states

    Descriptions
    ------------
    - Remove the active session belonging to <user>
    - Require token in the request header

    Returns
    -------
    msg: str
        indicating destruction status

    Raises
    ------
    HTTPException
        general endpoint error
    """
    
    try:
        states.pop(user["uid"])

        print(f"ALL STATES:\n{json.dumps(states, indent=4)}")

        return {"msg": "Session detroyed. User does not have any active chat session."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.post("/sanvia-chat/{thread_id}")
async def sanvia_chat(
    thread_id: str,
    request: PromptRequest,
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    
    """Message AI in Specific Chat
    
    Description
    -----------
    Authenticated Token is Needed in Request Header
    
    Parameters
    ----------
    thread_id: str
        Indicating which chat the message should go under

    Returns
    -------
    dict
        chat: str
            messages
        full_response: str
            ai response
        simple_response: str
            abstract ai response 
        total_sources: list[dict]
            all the references 
        sources: list[dict]
            references for ai response
        thread_id: str
            chat thread id

    Raises
    ------
    HTTPException 422
        prompt is not included, parameter value invalid
    HTTPException 404
        when the chat is not found / inactive
    HTTPException 400
        general codebase error
    """
    
    if request is None or request.prompt is None:
        raise HTTPException(status_code=422, detail=f"Request does not contain prompt for AI to work with.")

    
    try:
        # 1) Check if the chat [thread_id] is currently active in global state
        #       if not
        #           throw an error
        #       else
        #           get the state of the chat
        userid = user["uid"]
        if userid not in states.keys() or thread_id != states[userid]["thread_id"]:
            raise HTTPException(status_code=404, detail=f"Chat was not found.")
        
        _state = states[user["uid"]]
        _graph = initializeGraph(with_state=False)
        
        
        # 2) Append User Prompt to global states
        
        _state["prompt_chain"].append({"role": "user", "content": request.prompt})
        states[user["uid"]] = _state
        
        
        # 3) Generate AI response & Cleaning
        
        response = trigger_response(_graph, _state)
        full_response = response["prompt_chain"][-1]["content"]  # Last AI response

        # Modify response based on complexity choice
        simple_response = (
            " ".join(full_response.split()[:30]) + "..."
        )  # Shortened summary
        
        
        # 4) Update the Firestore entry of the chat [thread_id]
        update_chat_entry(
            user_id=user["uid"],
            thread_id=thread_id if _state["thread_id"] == thread_id else None,
            chat_data={
                "prompt_chain": _state["prompt_chain"],
                "sources": _state["knowledge"],
                "last_updated_at": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            },
        )
        
        
        # 5) HTTP Response
        return {
            "chat": _state["prompt_chain"],
            "full_response": full_response,  # Full text for "See More"
            "simple_response": simple_response,  # Now correctly accessible
            "total_sources": _state.get("knowledge", []),  # All sources used in the chat
            "sources": _state.get("shortterm_knowledge", []),  # Tavily search results
            "thread_id": _state["thread_id"],
        }

    except Exception as e:
        print(f"=========> ERROR: {e}")
        raise HTTPException(status_code=400, detail=f"Error: {e}")
        

@router.post("/create-chat")
async def create_chat_session(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    
    """Create new chat
    
    Descriptions
    ------------
    - User authentication is required, token needed in request header
    - Newly created chat would be both appended to LangGraph global states & uploaded onto Firestore
    - Any session user (global states) has would be replaced

    Returns
    -------
    dict
        msg: str
            indicating success/failure of chat creation
        thread_id: str
            thread_id of the newly created chat

    Raises
    ------
    HTTPException 400
        Chat creation encountered problem
    """
    
    try:
        
        # 1) Check if user has ongoing state in global state variable [aka user['uid'] exists in global states]
        #       if yes,
        #           replace with new one
        #       else,
        #           simply create new one
        
        thread_id, _graph, _state = create_new_thread(user=user)
        
        if user['uid'] not in states:
            states[user["uid"]] = {}
        
        states[user["uid"]][thread_id] = _state
        
        # 2) Upload thread onto Firestore
        
        update_chat_entry(
            user_id=user["uid"],
            thread_id=thread_id,
            chat_data={
                "prompt_chain": _state["prompt_chain"],
                "sources": _state["knowledge"],
                "last_updated_at": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            }
        )
        
        return {
            "msg": f"Chat created successfully",
            "thread_id": thread_id
        }
        
    except Exception as e:
        
        ## Clean up
        if user["uid"] in states and thread_id in states[user["uid"]]:
            del states[user["uid"]][thread_id]
        
        raise HTTPException(status=400, detail=f"Chat Creation Failed, error: {e}")

@router.get("/get-states")
async def getStates(key: str):
    if key == "404040":
        return states
    else:
        raise HTTPException(status_code=401)
    

@router.get("/chat/{thread_id}")
async def getChat(
    thread_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)], replace: bool = True
):
    """Retrieve Chat Data
    
    Descriptions
    ------------
    - User authentication needed, token attachment in request header required
    - Automatically replace the existing chat

    Parameters
    ----------
    thread_id : str
        referring to the chat that needs to be retrieved
    replace: bool
        indicating whether the current session would be replaced

    Returns
    -------
    dict
        chat: list[dict]
            list of messages in the chat
        thread_id: str
            thread_id

    Raises
    ------
    HTTPException 404
        thread_id was not provided, cannot retrieve without target
    HTTPException 400
        general endpoint error
    """
    if thread_id is None or thread_id.strip() == "":
        raise HTTPException(
            status_code=404, detail=f"Error: thread_id is not provided."
        )

    try:

        ## get thread data
        thread = get_chat(user_id=user["uid"], thread_id=thread_id)
        
        if not thread.exists:
            raise HTTPException(status_code=404, detail=f"Chat data not found.")

        ## check for session replacement
        if replace and user["uid"] in states.keys():
            states.pop(user["uid"])

        ## reinitialize session states for LangGraph
        # initialize every completely 
        _graph, _state = initializeGraph()
        _state["thread_id"] = thread_id
        _state["prompt_chain"] = (
            thread.to_dict()["prompt_chain"]
        )
        states[user["uid"]] = _state

        # print(f"ALL STATES:\n{json.dumps(states, indent=4)}")

        return {"chat": _state["prompt_chain"], "thread_id": _state["thread_id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")
