import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")


import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin.auth import verify_id_token
from firebase_admin import credentials, firestore
from datetime import datetime
from constants.credentials import FIREBASE_ADMIN_API_KEY
from constants.langgraph_obj import (
    AIBrain
)


def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized."""
    if not firebase_admin._apps:
        print(f"⏳⏳⏳ Initializing Firebase Admin SDK ⏳⏳⏳")
        cred = credentials.Certificate(FIREBASE_ADMIN_API_KEY)
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

def update_chat_entry(user_id: str, thread_id: str, chat_data: dict):
    """Update chat data of thread_id in Firestore"""
    doc_ref = get_firestore_client().collection("chat-history").document(user_id).collection("threads").document(thread_id)
    doc_ref.set(chat_data, merge=True)
    
def get_chat(user_id: str, thread_id: str):
    """Retrieve chat data of user_id/thread_id From Firestore"""
    doc_ref = get_firestore_client().collection("chat-history").document(user_id).collection("threads").document(thread_id)
    return doc_ref.get()
    
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
    token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> dict | None:
    """Uses a bearer token to identify Firebase user.

    Raises:
        HTTPException 401 if user does not exist or token is invalid.
    """
    try:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token Required.",
                headers={"WWW-Authenticate": "Bearer realm='Authentication Required'"},
            )
        user = verify_id_token(token.credentials)
        return user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not logged in or Invalid credentials",
            headers={"WWW-Authenticate": "Bearer realm='Invalid Token'"},
        )
        
        