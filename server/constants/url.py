import sys

sys.path.insert(2, "../constants")
from constants.credentials import FIREBASE_ADMIN_API_KEY, FIREBASE_WEB_API_KEY
import os

def firebase_rest(operation: str, api_key: str = FIREBASE_WEB_API_KEY):
    
    if api_key is None:
        raise ValueError("❌❌❌ API key is not set.")
    return f"https://identitytoolkit.googleapis.com/v1/accounts:{operation}?key={api_key}"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

SANVIA_BACKEND_BASE_URL = os.getenv("SANVIA_BACKEND_BASE_URL", "https://oauth-dev.sanvia.app")

WHOOP_BASE_URL = "https://api.prod.whoop.com/"