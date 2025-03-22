import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

from tavily import TavilyClient
from constants.credentials import TAVILY_API_KEY
from dependencies.tavily_dependencies import get_tavily_client

SEARCH_CATEGORIES = {
    "diagnosis": "diagnosis OR symptoms OR medical condition",
    "next_steps": "treatment OR management OR therapy",
    "research_papers": "research OR study OR clinical trial",
}

# Categorized list of trusted sources
TRUSTED_SOURCES = {
    "pubmed.ncbi.nlm.nih.gov": ["diagnosis", "research_papers"],
    "jamanetwork.com": ["diagnosis", "research_papers"],
    "nejm.org": ["research_papers"],
    "wolterskluwer.com": ["diagnosis", "next_steps"],
    "dynamed.com": ["diagnosis", "next_steps"],
    "ama-assn.org": ["diagnosis"],
    "cdc.gov": ["diagnosis", "next_steps"],
    "who.int": ["diagnosis", "next_steps", "research_papers"],
    "medscape.com": ["diagnosis", "next_steps"],
    "clinicaltrials.gov": ["research_papers"],
    "fda.gov": ["next_steps"],
    "ema.europa.eu": ["next_steps"],
    "nice.org.uk": ["next_steps", "research_papers"],
    "embase.com": ["research_papers"],
    "cochranelibrary.com": ["research_papers"],
    "ncbi.nlm.nih.gov/pmc": ["research_papers"],
    "europepmc.org": ["research_papers"],
    "uptodate.com": ["diagnosis", "next_steps"],
}


def tavily_search_function(query: str, category: str = None):
    """
    Perform a Tavily AI search with category filtering and return categorized sources.

    Args:
        query (str): The search query.
        category (str, optional): The category to filter by (diagnosis, next_steps, research_papers).

    Returns:
        list: A list of relevant search results with titles, URLs, and assigned categories.
    """
    try:
        response = get_tavily_client().search(query)

        results = []
        for r in response["results"]:
            domain = r["url"].split("/")[2]  # Extract domain name
            matched_categories = TRUSTED_SOURCES.get(domain, [])

            # Filter results based on requested category
            if category and category not in matched_categories:
                continue

            results.append(
                {"title": r["title"], "url": r["url"], "categories": matched_categories}
            )

        return results

    except Exception as e:
        raise Exception(f"Tavily search failed: {str(e)}")


# Initialize Tavily client with domain restrictions
def get_tavily_client():
    return TavilyClient(api_key=TAVILY_API_KEY, allowed_domains=TRUSTED_SOURCES)
