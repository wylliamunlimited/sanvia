# router.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from firebase_admin import auth
from server.config import get_firebase_user_from_token, update_survey_entry, db

router = APIRouter()


@router.get("/")
def hello():
    """Hello world route to test if the app is running."""
    return {"msg": "Hello World!"}


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the Firebase authenticated user ID."""
    return {"id": user["uid"]}


@router.post("/survey")
async def submit_survey(
    user: Annotated[dict, Depends(get_firebase_user_from_token)], survey_data: dict
):
    """Submits or updates a user's survey entry in Firestore."""
    update_survey_entry(user["uid"], survey_data)
    return {"msg": "Survey updated successfully"}


@router.get("/ehr/{patient_id}")
async def get_ehr_data(patient_id: str):
    """Fetches patient health data from an EHR system without storing it."""
    ehr_url = f"https://api.ehrprovider.com/fhir/Patient/{patient_id}"  # Replace with actual API

    try:
        response = requests.get(
            ehr_url, headers={"Authorization": "Bearer YOUR_EHR_ACCESS_TOKEN"}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch EHR data: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Checks the connection to Firebase Auth and Firestore."""
    try:
        # Check Firestore connection
        test_collection = db.collection("test").document("health_check").get()

        return {
            "firestore_status": (
                "Connected" if test_collection.exists else "No Data Found"
            ),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Firebase connection issue: {str(e)}"
        )
