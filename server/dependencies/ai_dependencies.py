import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

from langchain_openai import ChatOpenAI
from constants.credentials import OPENAI_API_KEY

def get_llm():
    """Return the LLM."""
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY,
        max_retries=3,
    )
