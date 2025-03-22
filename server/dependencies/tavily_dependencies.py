import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

import requests

from tavily import TavilyClient
from constants.credentials import TAVILY_API_KEY

# Initialize Tavily client with domain restrictions
def get_tavily_client():
    return TavilyClient(api_key=TAVILY_API_KEY, allowed_domains=TRUSTED_SOURCES)


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


def tavily_intense_search(
    query: str,
    topic: str = "general", ## general / news
    search_depth: str = "basic", ## basic / advanced
    chunks_per_source: int = 3, ## available only when 'search_depth' is advanced
    max_results: int = 5,
    time_range: None | str = None, ## default None
    days: int = 3,
    include_answer: bool = True,
    include_raw_content: bool = False,
    include_images: bool = False,
    include_image_descriptions: bool = False,
    include_domains: list = [],
    exclude_domains: list = []
) -> dict:
    """
    Perform an intense Tavily AI search with advanced options.
    
    Args:
        query (str): The search query.
        topic (str): The topic of the search (general / news).
        search_depth (str): The depth of the search (basic / advanced).
        chunks_per_source (int): Number of chunks to return per source.
        max_results (int): Maximum number of results to return.
        time_range (None | str, optional): Time range for the search (default None).
        days (int, optional): Number of days for the time range (default 3).
        include_answer (bool, optional): Whether to include a direct answer (default True).
        include_raw_content (bool, optional): Whether to include raw content from sources (default False).
        include_images (bool, optional): Whether to include images from sources (default False).
        include_image_descriptions (bool, optional): Whether to include image descriptions from sources (default False).
        include_domains (list, optional): List of domains to include in the search.
        exclude_domains (list, optional): List of domains to exclude from the search.
        
    Returns:
        dict: A dictionary containing the search results and any additional information.
            query: str
            answer: str
            images: []
                image.url: str
                image.description: str
            results: []
                result.title: str
                result.url: str
                result.content: str
                result.raw_content: str
                result.score: int
            response_time: int
    """
    
    try:
        
        response = get_tavily_client().search(
            query=query,
            topic=topic,
            search_depth=search_depth,
            chunks_per_source=chunks_per_source,
            max_results=max_results,
            time_range=time_range,
            days=days,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_image_descriptions=include_image_descriptions,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )

        return response
    except Exception as e:
        raise Exception(f"Tavily intense search failed: {str(e)}")