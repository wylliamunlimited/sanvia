import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")
import os
from functools import lru_cache
from typing import Dict, Optional, Any
from pydantic_settings import BaseSettings
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import auth
from firebase_admin.auth import verify_id_token
from firebase_admin import credentials, firestore
from constants.credentials import FIREBASE_ADMIN_API_KEY
from dependencies.firebase_dependencies import (
    get_firestore_client,
    get_firebase_user_from_token,
)
from dependencies.rag_dependencies import chroma_client
from fastapi import APIRouter
from google.cloud import storage
from google.oauth2 import service_account

router = APIRouter(prefix="/delete-user-data", tags=["delete-user-data"])
BUCKET_NAME = "sanvia-file-storage"


def delete_all_from_chroma(user_id: str):
    """Delete all vector embeddings for a user from ChromaDB"""
    collection = chroma_client.get_collection(name="prod_user_doc")
    collection.delete(where={"user_id": {"$eq": user_id}})
    return {"message": "User vector data deleted successfully"}


def delete_all_from_firestore(user: dict = Depends(get_firebase_user_from_token)):
    """Delete all Firestore documents for a user"""
    firestore_client = get_firestore_client()
    user_id = user["uid"]
    db = firestore_client.collection("users").document(user_id).collection("documents")
    docs = db.get()
    for doc in docs:
        doc.reference.delete()
    return {"message": "User firestore data deleted successfully"}


def delete_all_from_gcs(user: dict = Depends(get_firebase_user_from_token)):
    """Delete all GCS files for a user"""
    user_id = user["uid"]
    credentials = service_account.Credentials.from_service_account_info(
        FIREBASE_ADMIN_API_KEY
    )
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(BUCKET_NAME)
    blobs = bucket.list_blobs(prefix=f"documents/{user_id}/")
    for blob in blobs:
        blob.delete()
    return {"message": "User GCS data deleted successfully"}


@router.post("/delete-user-data")
async def delete_user_data(user: dict = Depends(get_firebase_user_from_token)):
    """Delete all user data from Firestore, ChromaDB, and GCS"""
    # Delete from all storage systems
    delete_all_from_gcs(user)
    delete_all_from_firestore(user)
    delete_all_from_chroma(user["uid"])

    return {"message": "User data deleted successfully from all storage systems"}


def delete_document_from_firestore(
    document_id: str, user: dict = Depends(get_firebase_user_from_token)
):
    firestore_client = get_firestore_client()
    user_id = user["uid"]

    # Delete from the correct Firestore collection
    doc_ref = (
        firestore_client.collection("documents")
        .document(user_id)
        .collection("files")
        .document(document_id)
    )

    # Check if document exists before deleting
    if doc_ref.get().exists:
        doc_ref.delete()

    return {"message": "Document deleted successfully from firestore"}


def delete_document_from_chroma(
    document_id: str, user: dict = Depends(get_firebase_user_from_token)
):
    """Delete a specific document's embeddings from ChromaDB"""
    user_id = user["uid"]
    collection = chroma_client.get_collection(name="prod_user_doc")
    # Delete all chunks associated with this document_id and user_id
    collection.delete(
        where={
            "$and": [
                {"user_id": {"$eq": user_id}},
                {"document_id": {"$eq": document_id}},
            ]
        }
    )
    return {"message": "Document embeddings deleted successfully from ChromaDB"}


def delete_document_from_gcs(
    document_id: str, user: dict = Depends(get_firebase_user_from_token)
):
    user_id = user["uid"]
    credentials = service_account.Credentials.from_service_account_info(
        FIREBASE_ADMIN_API_KEY
    )
    storage_client = storage.Client(credentials=credentials)
    db = get_firestore_client()
    bucket = storage_client.bucket(BUCKET_NAME)
    doc_ref = (
        db.collection("documents")
        .document(user_id)
        .collection("files")
        .document(document_id)
    )
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Document not found")

    document_data = doc.to_dict()
    gcs_path = document_data.get("gcs_path")
    blob = bucket.blob(gcs_path)

    try:
        blob.delete()
    except Exception as e:
        # If the file doesn't exist in GCS, we can ignore the error
        # since we still want to delete the Firestore record
        if "No such object" not in str(e):
            raise HTTPException(
                status_code=500, detail=f"Error deleting from GCS: {str(e)}"
            )

    return {"message": "Document deleted successfully from GCS"}


@router.post("/delete-document/{document_id}")
async def delete_document(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], document_id: str
):
    """Delete document from firestore, chroma and gcs"""
    delete_document_from_gcs(document_id, user)
    delete_document_from_firestore(document_id, user)
    delete_document_from_chroma(document_id, user)

    return {"message": "Document deleted successfully"}


def delete_individual_thread(
    thread_id: str, user: dict = Depends(get_firebase_user_from_token)
):
    """Delete a specific chat from firestore"""
    firestore_client = get_firestore_client()
    user_id = user["uid"]
    doc_ref = (
        firestore_client.collection("chat-history")
        .document(user_id)
        .collection("threads")
        .document(thread_id)
    )
    try:
        doc_ref.delete()
    except Exception as e:
        raise e
    return {"message": "Chat deleted successfully"}


@router.post("/delete-individual-chat/{thread_id}")
async def delete_individual_chat(
    thread_id: str, user: dict = Depends(get_firebase_user_from_token)
):
    """Delete a specific chat from firestore"""
    delete_individual_thread(thread_id, user)
    return {"message": "Chat deleted successfully"}


def delete_all_threads(user: dict = Depends(get_firebase_user_from_token)):
    """Delete all chats from firestore"""
    firestore_client = get_firestore_client()
    user_id = user["uid"]
    db = (
        firestore_client.collection("chat-history")
        .document(user_id)
        .collection("threads")
    )
    docs = db.get()
    for doc in docs:
        doc.reference.delete()
    return {"message": "All chats deleted successfully"}


@router.post("/delete-all-chats")
async def delete_all_chats(user: dict = Depends(get_firebase_user_from_token)):
    """Delete all chats from firestore"""
    delete_all_threads(user)
    return {"message": "All chats deleted successfully"}


def delete_user_account(user: dict = Depends(get_firebase_user_from_token)):
    """Delete user account from firestore and Firebase Authentication"""
    firestore_client = get_firestore_client()
    user_id = user["uid"]

    try:
        # First try to delete from Firebase Authentication
        try:
            auth.delete_user(user_id)
        except Exception as auth_error:
            print(f"Error deleting from Firebase Auth: {str(auth_error)}")
            # Continue even if Firebase Auth deletion fails, as the user might already be deleted

        # Delete user profile
        try:
            profile_doc = firestore_client.collection("profiles").document(user_id)
            if profile_doc.get().exists:
                profile_doc.delete()
        except Exception as profile_error:
            print(f"Error deleting profile: {str(profile_error)}")

        # Delete user documents
        try:
            docs_ref = (
                firestore_client.collection("documents")
                .document(user_id)
                .collection("files")
            )
            docs = docs_ref.get()
            for doc in docs:
                doc.reference.delete()
        except Exception as docs_error:
            print(f"Error deleting documents: {str(docs_error)}")

        return {
            "message": "Account deletion attempted. Some operations may have been skipped if data was already deleted."
        }
    except Exception as e:
        print(f"Unexpected error during account deletion: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error during account deletion: {str(e)}"
        )


@router.post("/delete-account")
async def delete_account(user: dict = Depends(get_firebase_user_from_token)):
    """Delete user account and all associated data"""
    # First delete all user data
    delete_all_from_gcs(user)
    delete_all_from_firestore(user)
    delete_all_from_chroma(user["uid"])
    delete_all_threads(user)

    # Then delete the account
    delete_user_account(user)
    return {"message": "Account and all associated data deleted successfully"}
