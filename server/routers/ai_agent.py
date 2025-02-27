import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")


from fastapi import APIRouter, Depends, HTTPException

from langgraph.graph import START, StateGraph, END

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from dependencies.ai_dependencies import get_llm


router = APIRouter()

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
