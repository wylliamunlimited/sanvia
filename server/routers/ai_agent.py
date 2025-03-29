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

@router.post("/ai-response")
async def ai_response(
    request: PromptRequest,
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    """
    Get AI response with Tavily-powered research sources and response complexity.
    """

    if request is None or request.prompt is None:
        return {"error": "No prompt provided."}

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
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.post("/destroy-chat-session")
async def destroy_chat_session(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    try:
        states.pop(user["uid"])

        print(f"ALL STATES:\n{json.dumps(states, indent=4)}")

        return {"msg": "Session detroyed. User does not have any active chat session."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.get("/chat")
async def getChat(
    thread_id: str, user: Annotated[dict, Depends(get_firebase_user_from_token)]
):
    """
    Retrieve the chat data specified by thread_id, activating and replacing existing chat session (if any) with it.
    """
    if thread_id is None or thread_id.strip() == "":
        raise HTTPException(
            status_code=400, detail=f"Error: thread_id is not provided."
        )

    try:

        ## get thread data
        thread = get_chat(user_id=user["uid"], thread_id=thread_id)

        ## check for session replacement
        if user["uid"] in states.keys():
            states.pop(user["uid"])

        ## reinitialize session states for LangGraph
        _graph, _state = initializeGraph()
        _state["thread_id"] = thread_id
        _state["prompt_chain"] = (
            thread.to_dict()["prompt_chain"]
            if thread.exists
            else _state["prompt_chain"]
        )
        states[user["uid"]] = _state

        print(f"ALL STATES:\n{json.dumps(states, indent=4)}")

        return {"chat": _state["prompt_chain"], "thread_id": _state["thread_id"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")


@router.get("/chat/{thread_id}")
async def get_thread(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], thread_id: str
):
    
    user_id = user['uid']
    
    try:
        
        pass
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {e}")