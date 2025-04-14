
import sys
sys.path.insert(2, "../constants")

from constants.credentials import (
    WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET
)
from constants.url import (
    WHOOP_BASE_URL, FRONTEND_URL
)
from fastapi import HTTPException

import json
import httpx
from datetime import datetime, timedelta

WHOOP_SLEEP_URL = WHOOP_BASE_URL + "developer/v1/activity/sleep"
WHOOP_USER_URL = WHOOP_BASE_URL + "developer/v1/user/profile/basic"
WHOOP_BODY_MEASUREMENT_URL = WHOOP_BASE_URL + "developer/v1/user/measurement/body"
WHOOP_CYCLE_URL = WHOOP_BASE_URL + "developer/v1/cycle"


async def get_whoop_sleep(access_token: str, start_days_ago: int = 7):
    
    """Get WHOOP Sleep data for user
    """
    
    headers = {
        "Authorization": f"Bearer {access_token}"
        }

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=start_days_ago)

    params = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            WHOOP_SLEEP_URL,
            params=params, 
            headers=headers
            )
        
    if res.status_code != 200:
        print(f"WHOOP sleep fetch failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch WHOOP sleep data")

    return res.json()

async def get_whoop_cycle(access_token: str, start_days_ago: int = 7):
    
    """Get WHOOP cycle data"""
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=start_days_ago)

    params = {
        "start": start_time.isoformat() + "Z",
        "end": end_time.isoformat() + "Z"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            WHOOP_CYCLE_URL,
            params=params,
            headers=headers
        )
        
    if res.status_code != 200:
        print(f"WHOOP cycle fetch failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch WHOOP cycle data")

    return res.json()

async def get_whoop_user(access_token: str):
    
    """Get WHOOP user information"""
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            WHOOP_USER_URL,
            headers=headers
        )
        
    if res.status_code != 200:
        print(f"WHOOP user information fetch failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch WHOOP user data")
    
    return res.json()

async def get_whoop_body_measurements(access_token: str):

    """Get WHOOP body measurements"""
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    async with httpx.AsyncClient() as client:
        res = await client.get(
            WHOOP_BODY_MEASUREMENT_URL,
            headers=headers
        )
        
    if res.status_code != 200:
        print(f"WHOOP user body measurement fetch failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch WHOOP user body measurements.")
    
    return res.json()