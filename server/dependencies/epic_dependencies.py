import sys
sys.path.insert(2, "../constants")


from constants.credentials import (
   EPIC_CLIENT_ID
)
from constants.url import (
   EPIC_BASE_URL, FRONTEND_URL
)
from fastapi import HTTPException
from typing import Dict
import json
import httpx
from datetime import datetime, timedelta




async def get_epic_patient_data(access_token: str, provider_url: str, patient_id: str) -> Dict:
   """Retrieve user overall information"""
   headers = {
       "Authorization": f"Bearer {access_token}"
       }


   async with httpx.AsyncClient() as client:
       res = await client.get(
           f"{provider_url}/{patient_id}",
           headers=headers
           )
      
   if res.status_code != 200:
       print(f"WHOOP sleep fetch failed: {res.text}")
       raise HTTPException(status_code=500, detail="Failed to fetch WHOOP sleep data")


   return res.json()
