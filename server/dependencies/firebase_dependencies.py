# config.py
import os
from dotenv import load_dotenv
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin.auth import verify_id_token
from firebase_admin import credentials, firestore
import json

# Load environment variables
load_dotenv()

# Check if GOOGLE_APPLICATION_CREDENTIALS is loaded
firebase_credentials_json = os.getenv("FIREBASE_ADMIN_SDK_KEY")
if firebase_credentials_json:
    print(f"✅ FIREBASE_ADMIN_SDK_KEY is Detected")
    firebase_credentials_json = json.loads(firebase_credentials_json)
else:
    print("❌ FIREBASE_ADMIN_SDK_KEY is NOT set.")
    raise ValueError("Firebase credentials file path is missing. Check your .env file.")


def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        print(f"⏳⏳⏳ Initializing Firebase Admin SDK ⏳⏳⏳")
        cred = credentials.Certificate(firebase_credentials_json)
        firebase_admin.initialize_app(cred)
    else:
        print("🔥🔥🔥 Firebase Admin SDK already initialized 🔥🔥🔥")


def get_firestore_client():
    """Retrieve Firestore client."""
    initialize_firebase()
    return firestore.client()


## this function should be under utils for sign up or database operation script [will come back and check]
def update_survey_entry(user_id: str, survey_data: dict):
    """Updates a user's survey entry in Firestore."""
    doc_ref = get_firestore_client().collection("surveys").document(user_id)
    doc_ref.set(survey_data, merge=True)


# Authentication setup (Bearer Token)
bearer_scheme = HTTPBearer(auto_error=False)


class Settings(BaseSettings):
    """Main app settings."""

    app_name: str = "demofirebase"
    env: str = os.getenv("ENV", "development")
    frontend_url: str = os.getenv("FRONTEND_URL", "NA")


@lru_cache
def get_settings() -> Settings:
    """Retrieve FastAPI settings."""
    return Settings()


def get_firebase_user_from_token(
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]
) -> dict | None:
    """Uses a bearer token to identify Firebase user.

    Raises:
        HTTPException 401 if user does not exist or token is invalid.
    """
    try:
        if not token:
            raise ValueError("No token provided")
        user = verify_id_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
