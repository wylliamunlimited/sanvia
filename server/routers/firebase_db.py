import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")


from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from firebase_admin import auth
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_survey_entry,
    get_firestore_client,
    update_name_entry,
    get_profile,
)
from constants.firestore_obj import Survey
from dependencies.survey_rag import store_survey_embeddings

router = APIRouter()


@router.post("/survey")
async def submit_survey(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], survey_data: dict
):
    """Submits or updates a user's survey entry in Firestore and processes it with RAG."""
    try:
        # Create Survey object
        survey = Survey(
            age=survey_data["age"],
            gender=survey_data["gender"],
            sex=survey_data["sex"],
            height=survey_data["height"],
            weight=survey_data["weight"],
        )

        # Update survey in Firestore
        update_survey_entry(user["uid"], survey)

        # Process survey data with RAG
        store_survey_embeddings(user["uid"], survey.to_dict())

        print(f"✅ Survey data processed and stored for user {user['uid']}")
        return {"msg": "Survey updated and processed successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Survey data upload failed: {str(e)}"
        )


@router.post("/store-names")
async def upload_names(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
    first_name: str,
    last_name: str,
):
    """Upload user's first & last name in Firestore."""
    try:
        update_name_entry(
            user_id=user["uid"], first_name=first_name, last_name=last_name
        )
        print(user["uid"])
        return {"msg": "Names updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"name data upload failed.")


@router.get("/get-profile")
async def get_user_profile(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    """Retrieve User's Profile From Firestore."""
    try:
        print(f"Retrieving data for {user['uid']}...")
        data = get_profile(user["uid"]).to_dict()
        return data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"user profile retrieval failed.")


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
