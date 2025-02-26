import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, '../dependencies')


from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from firebase_admin import auth
from dependencies.firebase_dependencies import get_firebase_user_from_token, update_survey_entry, get_firestore_client

router = APIRouter()

@router.post("/survey")
async def submit_survey(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], survey_data: dict
):
    """Submits or updates a user's survey entry in Firestore."""
    update_survey_entry(user["uid"], survey_data)
    return {"msg": "Survey updated successfully"}


@router.get("/firestore-health")
async def health_check():
    """Checks the connection to Firebase Auth and Firestore."""
    try:
        # Try fetching Firestore collections to confirm connectivity
        collections = get_firestore_client().collections()
        collections_list = [col.id for col in collections]

        return {
            "firestore_status": "Connected",
            "available_collections": collections_list,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Firebase connection issue: {str(e)}"
        )

