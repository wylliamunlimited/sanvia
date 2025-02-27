import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

from tavily import TavilyClient
from constants.credentials import TAVILY_API_KEY

# Initialize Tavily client
def get_tavily_client():
    """Return Tavily client."""
    return TavilyClient(api_key=TAVILY_API_KEY)

