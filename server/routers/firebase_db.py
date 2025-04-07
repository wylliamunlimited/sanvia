import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")


from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_survey_entry,
    get_firestore_client,
    update_name_entry,
    get_profile,
)
from constants.firestore_obj import Survey

router = APIRouter()


@router.post("/survey")
async def submit_survey(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], survey_data: dict
):
    """Submits or updates a user's survey entry in Firestore."""
    try: 
        update_survey_entry(user["uid"], Survey(
            age=survey_data['age'], gender=survey_data['gender'], sex=survey_data['sex'], height=survey_data['height'], 
            weight=survey_data['weight'], conditions=survey_data['conditions'], medications=survey_data['medications'],
        ))
        return {"msg": "Survey updated successfully"}
    except KeyError as ke:
        raise HTTPException(
            status_code=400, detail=("Invalid survey data format. Required Fields: age, "
                                     "gender, sex, height, weight, conditions, medications."
                                     "Please pass them in using JSON.")
        )
    except Exception as e:
        print(f"❌ Error submitting survey: {str(e)}")
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
        update_name_entry(user_id=user['uid'], first_name=first_name, last_name=last_name)
        return {"msg": "Names updated successfully"}
    except Exception as e:
        print(f"❌ Error uploading names: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"name data upload failed."
        )

@router.get("/get-profile")
async def get_user_profile(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
):
    """Retrieve User's Profile From Firestore."""
    try:
        print(f"Retrieving data for {user['uid']}...")
        profile_data = get_profile(user["uid"])

        if not profile_data:
            raise HTTPException(
                status_code=404,
                detail="Profile not found. Please complete the onboarding survey.",
            )

        return profile_data
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error retrieving profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve user profile. Please try again later.",
        )
        
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
