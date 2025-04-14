import sys

sys.path.insert(2, "../constants")
from constants.credentials import FIREBASE_ADMIN_API_KEY, FIREBASE_WEB_API_KEY
import os

def firebase_rest(operation: str, api_key: str = FIREBASE_WEB_API_KEY):
    
    if api_key is None:
        raise ValueError("❌❌❌ API key is not set.")
    return f"https://identitytoolkit.googleapis.com/v1/accounts:{operation}?key={api_key}"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

if FRONTEND_URL:
    print(f"✅ FRONTEND_URL is Detected")
else:
    print("❌ FRONTEND_URL is NOT set.")
    raise ValueError("Frontend URL is missing. Check your .env file.")



WHOOP_BASE_URL = "https://api.prod.whoop.com/"