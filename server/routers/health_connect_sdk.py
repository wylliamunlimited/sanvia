import os
import requests
from typing import List, Annotated
import sys
from datetime import datetime, timedelta

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException,
    Response,
    Request,
)
from fastapi.responses import StreamingResponse
from typing import List, Annotated, Dict, Any
from dependencies.health_connect_dependencies import HealthConnectDependencies
from dependencies.firebase_dependencies import get_firebase_user_from_token
from dependencies.auth_dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/health-connect",
    tags=["health-connect"],
    responses={404: {"description": "Not found"}},
)
health_connect = HealthConnectDependencies()


@router.post("/connect")
async def connect_health_connect(
    request: Request, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Connect user's Health Connect account"""
    return await health_connect.connect_health_connect(current_user.id)


@router.get("/oauth/callback")
async def health_connect_oauth_callback(
    request: Request,
    code: str,
    state: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Handle Health Connect OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = {
            "access_token": "placeholder_access_token",
            "refresh_token": "placeholder_refresh_token",
            "expires_in": 3600,
        }

        # Store tokens and update connection status
        user_ref = health_connect.db.collection("users").document(current_user.id)
        user_ref.update(
            {
                "health_connect.tokens": tokens,
                "health_connect.connected": True,
                "health_connect.connected_at": datetime.now().isoformat(),
            }
        )

        # Trigger initial sync
        await health_connect.sync_health_data(current_user.id)

        return {
            "status": "success",
            "message": "Health Connect connected successfully",
            "user_id": current_user.id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to complete OAuth flow: {str(e)}"
        )


@router.get("/sync")
async def sync_health_data(
    request: Request, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Sync all health data for the current user"""
    return await health_connect.sync_health_data(current_user.id)


@router.get("/sleep")
async def get_sleep_data(
    request: Request,
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get sleep data from Health Connect"""
    return await health_connect.get_sleep_data(current_user.id, start_time, end_time)


@router.get("/steps")
async def get_steps_data(
    request: Request,
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get steps data from Health Connect"""
    return await health_connect.get_steps_data(current_user.id, start_time, end_time)


@router.get("/heart-rate")
async def get_heart_rate_data(
    request: Request,
    start_time: datetime,
    end_time: datetime,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get heart rate data from Health Connect"""
    return await health_connect.get_heart_rate_data(
        current_user.id, start_time, end_time
    )
