
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
import xmltodict
import httpx
from datetime import datetime, timedelta


async def get_epic_patient_data(access_token: str, provider_url: str, patient_id: str) -> Dict:
    """Retrieve user overall information"""
    headers = {
        "Authorization": f"Bearer {access_token}"
        }
    
    print(f"Fetching EPIC patient data for patient {patient_id} from", f"{provider_url}/Patient/{patient_id}")

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{provider_url}/Patient/{patient_id}", ## format of provider_url: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
            headers=headers
            )
        
    if res.status_code != 200:
        print(f"EPIC user data fetch failed: {res.text}")
        raise HTTPException(status_code=500, detail="Failed to fetch EPIC user data")
    
    data = xmltodict.parse(res.text)
    return data

