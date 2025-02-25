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


# Load environment variables
load_dotenv()

# Check if GOOGLE_APPLICATION_CREDENTIALS is loaded
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if cred_path:
    print(f"✅ GOOGLE_APPLICATION_CREDENTIALS is set: {cred_path}")
else:
    print("❌ GOOGLE_APPLICATION_CREDENTIALS is NOT set.")
# Firebase Setup
firebase_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(firebase_credentials_path)
if not firebase_credentials_path:
    raise ValueError("Firebase credentials file path is missing. Check your .env file.")

# Initialize Firebase Admin SDK if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials_path)
    firebase_admin.initialize_app(cred)

# Firestore Client
db = firestore.client()


def update_survey_entry(user_id: str, survey_data: dict):
    """Updates a user's survey entry in Firestore."""
    doc_ref = db.collection("surveys").document(user_id)
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
