import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")


from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    get_firestore_client,
    get_profile,
    initialize_profile,
    update_profile,
)
from constants.firestore_obj import Survey

router = APIRouter()


@router.post("/initialize-profile")
async def initialize_user_profile(
    user: Annotated[dict, Depends(get_firebase_user_from_token)],
    profile_data: dict
):
    """Initialize user's profile in Firestore."""
    try:
        initialize_profile(
            user_id=user['uid'],
            first_name=profile_data['first_name'],
            last_name=profile_data['last_name']
        )
        return {"msg": "Profile initialized successfully"}
    except KeyError as ke:
        raise HTTPException(
            status_code=400, detail="Invalid profile data format. Required fields: first_name, last_name."
        )
    except Exception as e:
        print(f"❌ Error initializing profile: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Profile initialization failed."
        )

@router.post("/update-profile")
async def update_user_profile(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], survey_data: dict
):
    """Updates a user's profile in Firestore."""
    try: 
        update_profile(user["uid"], Survey(
            age=survey_data['age'], 
            gender=survey_data['gender'], 
            sex=survey_data['sex'], 
            height=survey_data['height'], 
            weight=survey_data['weight'], 
            conditions=survey_data['conditions'], 
            medications=survey_data['medications'],
            first_name=survey_data['first_name'],
            last_name=survey_data['last_name']
        ))
        return {"msg": "Profile updated successfully"}
    except KeyError as ke:
        raise HTTPException(
            status_code=400, detail=("Invalid profile data format. Required Fields: age, "
                                     "gender, sex, height, weight, conditions, medications, "
                                     "first_name, last_name. Please pass them in using JSON.")
        )
    except Exception as e:
        print(f"❌ Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Profile update failed: {str(e)}"
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
