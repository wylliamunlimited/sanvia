from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List
import uuid
import shutil
from server.dependencies.firebase_dependencies import (
    get_firestore_client,
    get_firebase_user_from_token,
)
from typing import Annotated

router = APIRouter()

# Directory to temporarily store documents (or use cloud storage)
UPLOAD_DIR = "uploaded_documents"


@router.post("/upload-document")
async def upload_document(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
    file: UploadFile = File(...),
):
    """Uploads a document and stores metadata in Firestore."""
    user_id = user["uid"]
    document_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{document_id}.pdf"

    # Save file temporarily
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Store metadata in Firestore
    db = get_firestore_client()
    doc_ref = (
        db.collection("documents")
        .document(user_id)
        .collection("files")
        .document(document_id)
    )
    doc_ref.set(
        {"document_id": document_id, "filename": file.filename, "user_id": user_id}
    )

    return {"message": "Document uploaded successfully", "document_id": document_id}


@router.get("/documents")
async def list_documents(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Fetches list of document names for the logged-in user."""
    user_id = user["uid"]
    db = get_firestore_client()
    docs = db.collection("documents").document(user_id).collection("files").stream()

    document_list = [
        {"document_id": doc.id, "filename": doc.to_dict().get("filename")}
        for doc in docs
    ]

    return {"documents": document_list}


@router.get("/document/{document_id}")
async def get_document(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], document_id: str
):
    """Retrieves a full document from Firestore."""
    user_id = user["uid"]
    db = get_firestore_client()
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
    return {"document": document_data}
