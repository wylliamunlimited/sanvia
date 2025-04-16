import os
from typing import List, Dict, Any
from fastapi import HTTPException
import requests
from datetime import datetime, timedelta
from dependencies.firebase_dependencies import get_firestore_client, get_profile
from models.health_data import HealthData


class HealthConnectDependencies:
    def __init__(self):
        self.health_connect_api_key = os.getenv("HEALTH_CONNECT_API_KEY")
        self.health_connect_base_url = "https://healthconnect.googleapis.com/v1"
        self.db = get_firestore_client()

    async def connect_health_connect(
        self, user_id: str, permissions: List[str] = None
    ) -> Dict[str, Any]:
        """Connect user's Health Connect account"""
        try:
            # Get user profile from Firestore
            user_profile = await get_profile(user_id=user_id)
            if not user_profile:
                raise HTTPException(status_code=404, detail="User profile not found")

            # Store Health Connect connection status
            health_connect_data = {
                "connected": True,
                "connected_at": datetime.now().isoformat(),
                "last_sync": None,
                "permissions": permissions or [],
                "device_id": user_profile.get("device_id", ""),
                "user_id": user_id,
            }

            # Update user profile with Health Connect data
            user_ref = self.db.collection("users").document(user_id)
            user_ref.update({"health_connect": health_connect_data})

            return {
                "status": "success",
                "message": "Health Connect connection successful",
                "user_id": user_id,
                "connected_at": health_connect_data["connected_at"],
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to connect Health Connect: {str(e)}"
            )

    async def store_health_data(self, health_data: HealthData) -> Dict[str, Any]:
        """Store health data in Firestore"""
        try:
            # Get user's Health Connect data
            user_ref = self.db.collection("users").document(health_data.user_id)
            user_data = user_ref.get().to_dict()

            if not user_data or not user_data.get("health_connect", {}).get(
                "connected"
            ):
                raise HTTPException(
                    status_code=400, detail="Health Connect not connected"
                )

            # Create a new document in the health_data collection
            health_data_ref = self.db.collection("health_data").document()

            # Convert the health data to a dictionary
            health_data_dict = health_data.dict()

            # Add metadata
            health_data_dict["received_at"] = datetime.now()
            health_data_dict["user_id"] = health_data.user_id
            health_data_dict["device_id"] = health_data.device_id

            # Store the data
            health_data_ref.set(health_data_dict)

            # Update last sync time
            user_ref.update({"health_connect.last_sync": datetime.now().isoformat()})

            return {
                "status": "success",
                "message": "Health data stored successfully",
                "data_id": health_data_ref.id,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to store health data: {str(e)}"
            )

    async def get_health_data(
        self, user_id: str, data_type: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get health data from Firestore"""
        try:
            # Get user's Health Connect data
            user_ref = self.db.collection("users").document(user_id)
            user_data = user_ref.get().to_dict()

            if not user_data or not user_data.get("health_connect", {}).get(
                "connected"
            ):
                raise HTTPException(
                    status_code=400, detail="Health Connect not connected"
                )

            # Query health data for the specified time range
            health_data_ref = self.db.collection("health_data")
            query = (
                health_data_ref.where("user_id", "==", user_id)
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

            return {
                "status": "success",
                "data_type": data_type,
                "user_id": user_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "data": health_data_list,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to get health data: {str(e)}"
            )

    async def get_sleep_data(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get sleep data from Firestore"""
        return await self.get_health_data(user_id, "sleep", start_time, end_time)

    async def get_steps_data(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get steps data from Firestore"""
        return await self.get_health_data(user_id, "steps", start_time, end_time)

    async def get_heart_rate_data(
        self, user_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Get heart rate data from Firestore"""
        return await self.get_health_data(user_id, "heart_rate", start_time, end_time)

    async def sync_health_data(self, user_id: str) -> Dict[str, Any]:
        """Sync all health data for a user"""
        try:
            # Get user's Health Connect data
            user_ref = self.db.collection("users").document(user_id)
            user_data = user_ref.get().to_dict()

            if not user_data or not user_data.get("health_connect", {}).get(
                "connected"
            ):
                raise HTTPException(
                    status_code=400, detail="Health Connect not connected"
                )

            # Get last sync time or default to 7 days ago
            last_sync = user_data.get("health_connect", {}).get("last_sync")
            if last_sync:
                start_time = datetime.fromisoformat(last_sync)
            else:
                start_time = datetime.now() - timedelta(days=7)

            end_time = datetime.now()

            # Sync all data types
            sleep_data = await self.get_sleep_data(user_id, start_time, end_time)
            steps_data = await self.get_steps_data(user_id, start_time, end_time)
            heart_rate_data = await self.get_heart_rate_data(
                user_id, start_time, end_time
            )

            # Update last sync time
            user_ref.update({"health_connect.last_sync": end_time.isoformat()})

            return {
                "status": "success",
                "message": "Health data synced successfully",
                "data": {
                    "sleep": sleep_data,
                    "steps": steps_data,
                    "heart_rate": heart_rate_data,
                },
            }
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to sync health data: {str(e)}"
            )
