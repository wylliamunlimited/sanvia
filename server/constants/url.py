import sys

sys.path.insert(2, "../constants")
from constants.credentials import FIREBASE_ADMIN_API_KEY, FIREBASE_WEB_API_KEY


def firebase_rest(operation: str, api_key: str = FIREBASE_WEB_API_KEY):
    
    if api_key is None:
        raise ValueError("❌❌❌ API key is not set.")
    return f"https://identitytoolkit.googleapis.com/v1/accounts:{operation}?key={api_key}"