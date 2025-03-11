from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import List, Annotated
import uuid
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes, convert_from_path
from PIL import Image
import os
import io
from datetime import datetime
from dependencies.firebase_dependencies import (
    get_firestore_client,
    get_firebase_user_from_token,
)

router = APIRouter()

POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin"  # Change to your Poppler path


def extract_text_with_ocr(file_bytes: io.BytesIO):
    """
    Extracts text from a PDF using PyMuPDF and OCR for scanned documents.
    """
    text_data = ""
    table_data = []

    try:
        # Read PDF into PyMuPDF
        doc = fitz.open(stream=file_bytes.getvalue(), filetype="pdf")

        for page in doc:
            page_text = page.get_text("text")

            if page_text.strip():  # If text is selectable, use it
                text_data += page_text + "\n"
            else:  # If no selectable text, use OCR
                print("🔍 No selectable text found, using OCR...")
                images = convert_from_bytes(
                    file_bytes.getvalue(), poppler_path=POPPLER_PATH
                )  # Convert PDF pages to images
                for image in images:
                    text_data += pytesseract.image_to_string(image) + "\n"

        return {"text": text_data, "tables": table_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/upload-document")
async def upload_document(
    user: dict = Depends(get_firebase_user_from_token), file: UploadFile = File(...)
):
    try:
        user_id = user["uid"]
        document_id = str(uuid.uuid4())  # Generate unique ID
        upload_date = datetime.utcnow().isoformat()  # Capture upload date

        print(f"📂 Received file: {file.filename} from user {user_id}")

        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Convert file to BytesIO for OCR processing
        file_bytes = io.BytesIO(await file.read())
        file_bytes.seek(0)  # ✅ Reset pointer to the beginning after reading

        # Extract text and tables
        pdf_content = extract_text_with_ocr(file_bytes)  # ✅ FIXED

        # Save metadata to Firestore
        db = get_firestore_client()
        doc_ref = (
            db.collection("documents")
            .document(user_id)
            .collection("files")
            .document(document_id)
        )

        metadata = {
            "filename": file.filename,
            "document_id": document_id,
            "user_id": user_id,
            "upload_date": upload_date,
            "content": pdf_content["text"],
            "tables": pdf_content["tables"],
        }

        doc_ref.set(metadata)
        print(f"🔥 Metadata and content saved for {file.filename}")

        return {
            "filename": file.filename,
            "document_id": document_id,
            "msg": "File processed and stored successfully",
            "upload_date": upload_date,
        }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Fetches list of document names for the logged-in user."""
    user_id = user["uid"]
    db = get_firestore_client()
    docs = db.collection("documents").document(user_id).collection("files").stream()

    document_list = [
        {
            "document_id": doc.id,
            "filename": doc.to_dict().get("filename"),
            "upload_date": doc.to_dict().get("upload_date"),
        }
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
    return {
        "filename": document_data["filename"],
        "upload_date": document_data["upload_date"],
        "content": document_data["content"],
        "tables": document_data["tables"],
    }
