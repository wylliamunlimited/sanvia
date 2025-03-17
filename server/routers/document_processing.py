from typing import List, Annotated
import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import List, Annotated
import uuid
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_bytes
from google.cloud import storage
import os
from google.oauth2 import service_account
import io
from datetime import datetime, timedelta
from dependencies.firebase_dependencies import (
    get_firestore_client,
    get_firebase_user_from_token,
)
from constants.credentials import FIREBASE_ADMIN_API_KEY

from constants.utils import POPPLER_PATH

router = APIRouter()


BUCKET_NAME = "sanvia-file-storage"  # Google Cloud Storage bucket


def upload_to_gcs(file_bytes, destination_blob_name):
    """Uploads a file to Google Cloud Storage and returns a signed URL."""
    try:
        # credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        # if not credentials_path:
        #     raise ValueError("❌ GOOGLE_APPLICATION_CREDENTIALS is not set in .env!")

        credentials = service_account.Credentials.from_service_account_info(
            FIREBASE_ADMIN_API_KEY
        )

        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(destination_blob_name)

        # Upload from memory
        blob.upload_from_file(file_bytes, content_type="application/pdf")

        # Generate a signed URL (valid for 1 hour)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),  # URL expires in 1 hour
            method="GET",
        )

        print(f"✅ File uploaded to {signed_url}")
        return signed_url  # Return signed URL instead of public URL
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
        upload_date = datetime.now().isoformat()

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
            "gcs_path": gcs_path,
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


def download_from_gcs(gcs_path):
    """
    Streams the PDF file directly from Google Cloud Storage.
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_path)

        file_data = blob.download_as_bytes()  # Download as bytes

        return io.BytesIO(file_data)  # Convert to a streamable object
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")


@router.get("/document/{document_id}")
async def get_document(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], document_id: str
):
    """Streams the complete PDF file to the frontend for display."""
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
    gcs_path = document_data.get("gcs_path")

    if not gcs_path:
        raise HTTPException(status_code=500, detail="File path not found in Firestore")

    # Download PDF from GCS
    pdf_stream = download_from_gcs(gcs_path)

    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{document_data["filename"]}"'
        },
    )


@router.get("/documents")
async def list_documents(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Fetches list of document names for the logged-in user."""
    user_id = user["uid"]
    db = get_firestore_client()
    docs = db.collection("documents").document(user_id).collection("files").stream()

    document_list = []
    for doc in docs:
        data = doc.to_dict()
        data["document_id"] = doc.id  # Add document id to metadata
        document_list.append(data)

    return {"documents": document_list}

def generate_signed_url(gcs_path):
     """
     Generate a signed URL for secure temporary access to the file in GCS.
     """
     try:
         storage_client = storage.Client()
         bucket = storage_client.bucket(BUCKET_NAME)
         blob = bucket.blob(gcs_path)
 
         signed_url = blob.generate_signed_url(
             version="v4",
             expiration=timedelta(minutes=30),  # URL expires in 30 minutes
             method="GET",
         )
         return signed_url
     except Exception as e:
         raise HTTPException(
             status_code=500, detail=f"Error generating signed URL: {str(e)}"
         )

@router.get("/document/{document_id}/signed-url")
async def get_fresh_signed_url(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], document_id: str
):
    """Generates a fresh signed URL for a document, allowing preview refresh."""
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
    gcs_path = document_data.get("gcs_path")

    if not gcs_path:
        raise HTTPException(status_code=500, detail="File path not found in Firestore")

    # Generate a fresh signed URL
    fresh_signed_url = generate_signed_url(gcs_path)

    return {
        "document_id": document_id,
        "signed_url": fresh_signed_url,
        "expires_in": 1800,  # 30 minutes in seconds
    }