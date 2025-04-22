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
from datetime import datetime, timedelta
from constants.credentials import FIREBASE_ADMIN_API_KEY
from constants.firestore_obj import Survey
from constants.langgraph_obj import AIBrain
from constants.firestore_obj import (
    WhoopTokenData
)

def get_survey_context(survey_data: Dict) -> str:
    """Convert survey data into a structured text format for embedding."""
    return f"""Patient Profile: Age: {survey_data['Age']} Gender: {survey_data['Gender']} Sex: {survey_data['Sex']} Height: {survey_data['Height']}cm Weight: {survey_data['Weight']}kg"""


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK if not already initialized."""
    try:
        if not firebase_admin._apps:
            print(f"⏳⏳⏳ Initializing Firebase Admin SDK ⏳⏳⏳")
            cred = credentials.Certificate(FIREBASE_ADMIN_API_KEY)
            firebase_admin.initialize_app(cred)
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
        if not doc.exists:
            return None
        return doc
    except Exception as e:
        print(f"❌ Error getting chat: {str(e)}")
        raise


def get_all_chat_threads(user_id: str):
    """Retrieve all chat threads for a user from Firestore"""
    collection_ref = (
        get_firestore_client()
        .collection("chat-history")
        .document(user_id)
        .collection("threads")
    )
    return collection_ref.stream()


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
    """Verifies Firebase bearer token and returns user info.

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired.
    """
    if token is None:
        raise _unauthorized_exception("Token required.")

    initialize_firebase()

    try:
        return verify_id_token(token.credentials, check_revoked=True)
    except Exception as e:
        print(f"❌ Firebase token verification failed: {e}")
        raise _unauthorized_exception("Invalid or expired token.")


def _unauthorized_exception(detail: str) -> HTTPException:
    """Returns a standardized 401 HTTPException."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer realm='Authentication Required'"},
    )



def update_whoop_tokens(user_id: str, token_data: dict):
    
    """Store WHOOP Authentication Token Pair & Metadata
    
    Format:
        access_token: str
        refresh_token: str
        expires_in: int
        scope: str
        token_type: str
    """
    
    try:
        ## TODO: encrypt refresh token
        whoop_token_data = WhoopTokenData(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            scope=token_data["scope"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            expiration_date=datetime.utcnow() + timedelta(seconds=token_data["expires_in"]),
            last_updated=datetime.utcnow(),
        )
        
        ## get list of token 
        token_history = get_whoop_tokens(user_id=user_id)
        
        token_history.append(whoop_token_data.to_dict())
        
        doc_ref = get_firestore_client().collection("whoop-tokens").document(user_id)
        doc_ref.set({"tokens": token_history}, merge=True)
        
        return {
            "access_token": whoop_token_data.access_token,
            "expiration_date": whoop_token_data.expiration_date,
        }
    except KeyError as ke:
        print(f"Key Error - Whoop Token Data missing value: {ke}")
        raise HTTPException(status_code=400, detail=f"Whoop authorization data corrupted.")
    except Exception as e:
        print(f"❌ Whoop authorization error: {str(e)}")



def get_whoop_tokens(user_id: str):
    """Retrieve WHOOP Authorization Token data from Firestore
    
    Format:
        access_token: str
        refresh_token: str
        expires_in: int
        scope: str
        token_type: str
        last_updated: datetime
        expiration_date: datetime
    """
    
    try:
        doc_ref = get_firestore_client().collection("whoop-tokens").document(user_id)
        doc = doc_ref.get() ## returning {"tokens": [...]}
        
        if not doc.exists:
            return []
        
        token_history = doc.to_dict().get("tokens", [])

        # Return the list of token
        return token_history

    except Exception as e:
        print(f"Error retrieving WHOOP token information: {e}")
        raise HTTPException(status_code=500, detail="Database: WHOOP Token Retrieval Failed.")
    
    
def get_recent_whoop_token(user_id: str):
    token_history = get_whoop_tokens(user_id=user_id)
    return token_history[-1]