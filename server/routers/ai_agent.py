import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")


from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Dict
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token
)
from dependencies.ai_dependencies import get_llm, initializeGraph, trigger_response, AIBrain
from pydantic import BaseModel
from langgraph.graph import StateGraph

import random ## TO BE REMOVED
from datetime import datetime

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str
    # thread_id: str = None ## Temporary


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
@router.post("/ai-response")
async def ai_response(
                        request: PromptRequest, 
                        user: Annotated[dict, Depends(get_firebase_user_from_token)]
                    ):
    """
    Get AI response based on the provided prompt.
    """
    
    if request is None or request.prompt is None:
        return {"error": "No prompt provided."}
    
    ## AUTHENTICATION NEEDED HERE
    if user["uid"] not in states:
        ## make a graph for this user
        thread_id = user['uid'] + datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(0, 1000))
        _graph, _state = initializeGraph()
        _state["thread_id"] = thread_id
        states[user["uid"]] = _state
    else:
        _graph = initializeGraph(with_state=False)
        _state = states[user["uid"]]
        
    # print(f"OLD STATE: {_state}\n\n")
    
    ## Include the new message
    _state["prompt_chain"].append({"role": "user", "content": request.prompt})
    states[user["uid"]] = _state
    
    # print(f"NEW STATE: {_state}\n\n")
    
    response = trigger_response(_graph, _state)
    
    print(f"ALL STATES:\n{states}")
    
    return {"chat": response["prompt_chain"]}

@router.post("/destroy-chat-session")
async def destroy_chat_session(
                            user: Annotated[dict, Depends(get_firebase_user_from_token)]
                        ):
    try:
        states.pop(user["uid"])
        
        print(f"ALL STATES:\n{states}")
        
        return {
            "msg": "Session detroyed. User does not have any active chat session."
        }
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"This user does not have a chat session. Error: {e}"
        )
        

# @router.post("/ai-response")
# async def ai(request: PromptRequest):
#     pass