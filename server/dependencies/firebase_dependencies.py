import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(2, "../constants")


import os
from functools import lru_cache
from typing import Dict, Optional, Any
from pydantic_settings import BaseSettings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin.auth import verify_id_token
from firebase_admin import credentials, firestore
from datetime import datetime
from constants.credentials import FIREBASE_ADMIN_API_KEY
from constants.firestore_obj import Survey
from constants.langgraph_obj import AIBrain


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK if not already initialized."""
    try:
        if not firebase_admin._apps:
            print(f"⏳⏳⏳ Initializing Firebase Admin SDK ⏳⏳⏳")
            cred = credentials.Certificate(FIREBASE_ADMIN_API_KEY)
            firebase_admin.initialize_app(cred)
        else:
            print("🔥🔥🔥 Firebase Admin SDK already initialized 🔥🔥🔥")
    except Exception as e:
        print(f"❌ Error initializing Firebase: {str(e)}")
        raise


def get_firestore_client() -> firestore.Client:
    """Retrieve Firestore client."""
    try:
        initialize_firebase()
        return firestore.client()
    except Exception as e:
        print(f"❌ Error getting Firestore client: {str(e)}")
        raise


## this function should be under utils for sign up or database operation script [will come back and check]
def update_survey_entry(user_id: str, survey_data: Survey) -> None:
    """Updates a user's survey entry in Firestore."""
    try:
        doc_ref = get_firestore_client().collection("profiles").document(user_id)
        doc_ref.set(survey_data.to_dict(), merge=True)
    except Exception as e:
        print(f"❌ Error updating survey entry: {str(e)}")
        raise


def update_name_entry(user_id: str, first_name: str, last_name: str) -> None:
    """Updates a user's first & last names in Firestore."""
    try:
        doc_ref = get_firestore_client().collection("profiles").document(user_id)
        doc_ref.set({"first-name": first_name, "last-name": last_name}, merge=True)
    except Exception as e:
        print(f"❌ Error updating name entry: {str(e)}")
        raise


def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve User's Profile From Firestore"""
    try:
        doc_ref = get_firestore_client().collection("profiles").document(user_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"❌ Error getting profile: {str(e)}")
        raise


def update_chat_entry(user_id: str, thread_id: str, chat_data: Dict[str, Any]) -> None:
    """Update chat data of thread_id in Firestore"""
    try:
        doc_ref = (
            get_firestore_client()
            .collection("chat-history")
            .document(user_id)
            .collection("threads")
            .document(thread_id)
        )
        doc_ref.set(chat_data, merge=True)
    except Exception as e:
        print(f"❌ Error updating chat entry: {str(e)}")
        raise


def get_chat(user_id: str, thread_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve chat data of user_id/thread_id From Firestore"""
    try:
        doc_ref = (
            get_firestore_client()
            .collection("chat-history")
            .document(user_id)
            .collection("threads")
            .document(thread_id)
        )
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    except Exception as e:
        print(f"❌ Error getting chat: {str(e)}")
        raise


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
) -> Dict[str, Any]:
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
        user = verify_id_token(token.credentials, check_revoked=True)

        # print("Decoded Firebase User:", user)
        return user
    except Exception as e:
        print(f"❌ Error verifying Firebase token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer realm='Authentication Required'"},
        )
