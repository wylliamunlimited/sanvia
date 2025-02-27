import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")

from fastapi import APIRouter, Depends, HTTPException, status
from dependencies.tavily_dependencies import get_tavily_client


router = APIRouter()

@router.get("/tavily-health")
async def health_check():
    """
    Search for a query in the database.
    """
    try:
        
        response = get_tavily_client().search("test")

        return {
            "tavily_status": "Connected",
            "search_result_count": len(response["results"])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tavily connection issue: {str(e)}"
        )