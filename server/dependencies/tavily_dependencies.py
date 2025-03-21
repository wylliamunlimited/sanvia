import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")

from tavily import TavilyClient
from constants.credentials import TAVILY_API_KEY

# List of trusted sources
TRUSTED_SOURCES = [
    "pubmed.ncbi.nlm.nih.gov",
    "jamanetwork.com",
    "nejm.org",
    "wolterskluwer.com",
    "dynamed.com",
    "ama-assn.org",
    "cdc.gov",
    "who.int",
    "medscape.com",
    "clinicaltrials.gov",
    "fda.gov",
    "ema.europa.eu",
    "nice.org.uk",
    "embase.com",
    "cochranelibrary.com",
    "ncbi.nlm.nih.gov/pmc",
    "europepmc.org",
    "uptodate.com",
]


# Initialize Tavily client with domain restrictions
def get_tavily_client():
    return TavilyClient(api_key=TAVILY_API_KEY, allowed_domains=TRUSTED_SOURCES)
