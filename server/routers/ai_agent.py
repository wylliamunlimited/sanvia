import sys

from openai import BaseModel

from server.dependencies.tavily_dependencies import get_tavily_client

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
    update_chat_entry,
    get_chat,
)
from constants.request_obj import PromptRequest
from dependencies.ai_dependencies import (
    get_llm,
    initializeGraph,
    trigger_response,
    AIBrain,
)
from langchain_core.messages import HumanMessage  # ✅ Correct Import
import random  ## TO BE REMOVED
from datetime import datetime
import json
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
    complexity: str = "simple",  # User can choose "simple" or "complex"
    expand: bool = False,  # Toggle to show more/less
):
    """
    Get AI response with an option for complexity and expandable summaries.
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
        if complexity == "simple":
            simple_response = (
                " ".join(full_response.split()[:30]) + "..."
            )  # Trim response
        else:
            simple_response = full_response  # Full response

        # Apply "See More/Less" logic
        if expand:
            final_response = full_response  # Show full response
        else:
            final_response = (
                " ".join(full_response.split()[:50]) + "..."
            )  # Shortened preview

        # 🔍 Fetch relevant sources
        search_results = get_tavily_client().search(request.prompt)
        sources = [
            {"title": r["title"], "url": r["url"]}
            for r in search_results["results"][:3]
        ]

        # Save chat to Firestore
        update_chat_entry(
            user_id=user["uid"],
            thread_id=_state["thread_id"],
            chat_data={
                "prompt_chain": _state["prompt_chain"],
                "sources": sources,
                "last_updated_at": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
            },
        )

        return {
            "chat": _state["prompt_chain"],
            "response": final_response,
            "full_response": full_response,  # Full text for "See More"
            "complexity": complexity,
            "expand": expand,
            "sources": sources,
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
