from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timedelta
from models.health_data import HealthData
from dependencies.firebase_dependencies import get_firebase_user_from_token
from dependencies.auth_dependencies import get_current_user
from models.user import User
from firebase_admin import firestore

router = APIRouter(
    prefix="/api/health-data",
    tags=["health-data"],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def receive_health_data(
    health_data: HealthData, current_user: User = Depends(get_current_user)
):
    """Receive health data from the Android app"""
    try:
        # Verify the user ID matches the current user
        if health_data.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="User ID mismatch")

        # Get Firestore client
        db = firestore.client()

        # Create a new document in the health_data collection
        health_data_ref = db.collection("health_data").document()

        # Convert the health data to a dictionary
        health_data_dict = health_data.dict()

        # Add metadata
        health_data_dict["received_at"] = datetime.now()
        health_data_dict["user_id"] = current_user.id
        health_data_dict["device_id"] = health_data.device_id

        # Store the data
        health_data_ref.set(health_data_dict)

        return {"status": "success", "message": "Health data received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_health_data(
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
):
    """Get health data for a specific time range"""
    try:
        # Get Firestore client
        db = firestore.client()

        # Query health data for the specified time range
        health_data_ref = db.collection("health_data")
        query = (
            health_data_ref.where("user_id", "==", current_user.id)
            .where("timestamp", ">=", start_time)
            .where("timestamp", "<=", end_time)
        )

        # Execute the query
        docs = query.stream()

        # Convert documents to HealthData objects
        health_data_list = []
        for doc in docs:
            data = doc.to_dict()
            health_data_list.append(HealthData(**data))

        return {"status": "success", "data": health_data_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
