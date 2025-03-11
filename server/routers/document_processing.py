from typing import List, Annotated
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import uuid
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
import io
from datetime import datetime
from google.cloud import storage
from dependencies.firebase_dependencies import (
    get_firestore_client,
    get_firebase_user_from_token,
)

router = APIRouter()

BUCKET_NAME = "sanvia-file-storage"  # Google Cloud Storage bucket


def upload_to_gcs(file_bytes: io.BytesIO, destination_blob_name: str):
    """Uploads a file to Google Cloud Storage and returns its URL."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        # Upload file from memory
        blob.upload_from_file(file_bytes, content_type="application/pdf")

        # Make the file publicly accessible (optional)
        blob.make_public()

        return blob.public_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading to GCS: {str(e)}")


def extract_text_with_ocr(file_bytes: io.BytesIO):
    """Extracts text from a PDF using PyMuPDF and OCR for scanned documents."""
    text_data = ""

    try:
        doc = fitz.open(stream=file_bytes.getvalue(), filetype="pdf")
        for page in doc:
            page_text = page.get_text("text")

            if page_text.strip():
                text_data += page_text + "\n"
            else:
                print("🔍 No selectable text found, using OCR...")
                images = convert_from_bytes(file_bytes.getvalue())
                for image in images:
                    text_data += pytesseract.image_to_string(image) + "\n"

        return text_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.post("/upload-document")
async def upload_document(
    user: dict = Depends(get_firebase_user_from_token), file: UploadFile = File(...)
):
    """Uploads a PDF to GCS, extracts text with OCR, and saves metadata in Firestore."""
    try:
        user_id = user["uid"]
        document_id = str(uuid.uuid4())
        upload_date = datetime.utcnow().isoformat()

        print(f"📂 Received file: {file.filename} from user {user_id}")

        # Validate file type
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Convert file to BytesIO for GCS upload and OCR
        file_bytes = io.BytesIO(await file.read())

        # Define GCS path: documents/{user_id}/{document_id}.pdf
        gcs_path = f"documents/{user_id}/{document_id}.pdf"

        # Upload to Google Cloud Storage
        gcs_url = upload_to_gcs(file_bytes, gcs_path)

        # Extract text from the uploaded file
        file_bytes.seek(0)  # Reset pointer for OCR processing
        extracted_text = extract_text_with_ocr(file_bytes)

        # Save metadata + extracted text in Firestore
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
            "gcs_url": gcs_url,
            "extracted_text": extracted_text,  # Store OCR text in Firestore
        }

        doc_ref.set(metadata)
        print(f"🔥 Metadata + OCR text saved for {file.filename}")

        return {
            "filename": file.filename,
            "document_id": document_id,
            "msg": "File uploaded, processed, and stored successfully",
            "upload_date": upload_date,
            "gcs_url": gcs_url,
            "extracted_text": extracted_text[
                :500
            ],  # Return only first 500 chars for preview
        }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


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
