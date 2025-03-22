import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")

from fastapi import APIRouter, Depends, HTTPException, status, Query
from dependencies.tavily_dependencies import get_tavily_client, tavily_search_function


router = APIRouter()

SEARCH_CATEGORIES = {
    "diagnosis": "diagnosis OR symptoms OR medical condition",
    "next_steps": "treatment OR management OR therapy",
    "research_papers": "research OR study OR clinical trial",
}


@router.get("/tavily-health")
async def health_check():
    """
    Search for a query in the database.
    """
    try:

        response = get_tavily_client().search("test")

        return {
            "tavily_status": "Connected",
            "search_result_count": len(response["results"]),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Tavily connection issue: {str(e)}"
        )


@router.get("/tavily-search")
async def tavily_search(
    query: str,
    category: str = Query(None, enum=["diagnosis", "next_steps", "research_papers"]),
):
    """
    Searches for medical information using Tavily AI, filtered by category.
    """
    try:
        results = tavily_search_function(query, category)
        return {"query": query, "category": category, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
