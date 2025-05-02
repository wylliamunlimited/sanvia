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


async def get_epic_medical_conditions(access_token: str, provider_url: str, patient_id: str) -> Dict:
    """
    Retrieve medical history conditions for a patient using FHIR R4 API.
    
    Args:
        access_token (str): OAuth access token
        provider_url (str): Base URL of the FHIR provider
        patient_id (str): Patient's FHIR ID
        
    Returns:
        Dict: Medical conditions data in FHIR R4 format
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    print(f"Fetching EPIC medical conditions for patient {patient_id} from", 
          f"{provider_url}/Condition?patient={patient_id}&category=medical-history")

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{provider_url}/Condition",
            headers=headers,
            params={
                "patient": patient_id,
            }
        )
        
    if res.status_code != 200:
        print(f"EPIC medical conditions fetch failed: {res.text}")
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Failed to fetch EPIC medical conditions: {res.text}"
        )
    
    data = res.json()
    return extract_non_suppressed_conditions(data)



def extract_non_suppressed_conditions(bundle):
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Not a valid FHIR Bundle")

    clean_conditions = []

    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})

        # Skip OperationOutcome entries (suppressed data, warnings, etc.)
        if resource.get("resourceType") != "Condition":
            continue

        # Build simplified output (you can expand this as needed)
        condition = {
            "id": resource.get("id"),
            "text": resource.get("code", {}).get("text"),
            "codes": [c["code"] for c in resource.get("code", {}).get("coding", [])],
            "categories": [
                cat.get("text") for cat in resource.get("category", [])
            ],
            "status": resource.get("clinicalStatus", {}).get("text"),
            "onset": resource.get("onsetDateTime"),
            "recorded": resource.get("recordedDate"),
        }

        clean_conditions.append(condition)

    return clean_conditions


async def make_epic_fhir_request(access_token: str, provider_url: str, suffix: str, params: Dict = None) -> Dict:
    """
    Make a generic FHIR API request to Epic.
    
    Args:
        access_token (str): OAuth access token
        provider_url (str): Base URL of the FHIR provider
        suffix (str): The API endpoint suffix (e.g., "Observation/123", "Patient/456")
        params (Dict, optional): Query parameters for the request
        
    Returns:
        Dict: FHIR resource data in JSON format
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    print(f"Making EPIC FHIR request to {provider_url}/{suffix}")

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{provider_url}/{suffix}",
            headers=headers,
            params=params or {}
        )
        
    if res.status_code != 200:
        print(f"EPIC FHIR request failed: {res.text}")
        raise HTTPException(
            status_code=res.status_code,
            detail=f"Failed to fetch EPIC FHIR data: {res.text}"
        )
    
    return res.json()


async def get_epic_diagnostic_reports(access_token: str, provider_url: str, patient_id: str) -> Dict:
    """
    Retrieve diagnostic reports for a patient using FHIR R4 API.
    """
    data = await make_epic_fhir_request(
        access_token=access_token,
        provider_url=provider_url,
        suffix="DiagnosticReport",
        params={"patient": patient_id}
    )
    return await extract_non_suppressed_diagnostic_reports(data, access_token, provider_url)


async def extract_non_suppressed_diagnostic_reports(bundle, access_token: str, provider_url: str):
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Not a valid FHIR Bundle")

    clean_reports = []

    for entry in bundle.get("entry", []):
        try:
            resource = entry.get("resource", {})

            # Skip OperationOutcome entries (suppressed data, warnings, etc.)
            if resource.get("resourceType") != "DiagnosticReport":
                continue

            # Check if this is a lab report
            is_lab_report = False
            for category in resource.get("category", []):
                category_text = category.get("text", "").lower()
                if category_text in ["lab", "laboratory"]:
                    is_lab_report = True
                    break

            # Skip non-lab reports
            if not is_lab_report:
                continue

            # Fetch observation results
            observation_results = []
            for result_ref in resource.get("result", []):
                try:
                    observation_id = result_ref.get("reference").split("/")[-1]
                    observation = await make_epic_fhir_request(
                        access_token=access_token,
                        provider_url=provider_url,
                        suffix=f"Observation/{observation_id}"
                    )
                    if observation and observation.get("resourceType") == "Observation":
                        observation_results.append(observation)
                except Exception as e:
                    print(f"Failed to fetch observation {result_ref.get('reference')}: {str(e)}")
                    continue

            # Fetch presented forms (binary data)
            presented_forms = []
            for form in resource.get("presentedForm", []):
                try:
                    binary_id = form.get("url").split("/")[-1]
                    binary_data = await make_epic_fhir_request(
                        access_token=access_token,
                        provider_url=provider_url,
                        suffix=f"Binary/{binary_id}"
                    )
                    if binary_data and binary_data.get("resourceType") == "Binary":
                        presented_forms.append({
                            "contentType": form.get("contentType"),
                            "data": binary_data
                        })
                except Exception as e:
                    print(f"Failed to fetch binary data {form.get('url')}: {str(e)}")
                    continue

            # Only include reports that have successfully fetched data
            if observation_results or presented_forms:
                report = {
                    "id": resource.get("id"),
                    "status": resource.get("status"),
                    "category": [cat.get("text") for cat in resource.get("category", [])],
                    "code": {
                        "text": resource.get("code", {}).get("text"),
                        "codes": [c["code"] for c in resource.get("code", {}).get("coding", [])]
                    },
                    "subject": resource.get("subject", {}).get("reference"),
                    "effectiveDateTime": resource.get("effectiveDateTime"),
                    "issued": resource.get("issued"),
                    "performer": [
                        perf.get("display") for perf in resource.get("performer", [])
                    ],
                    "results": observation_results,
                    "conclusion": resource.get("conclusion"),
                    "presentedForm": presented_forms
                }
                clean_reports.append(report)
        except Exception as e:
            print(f"Failed to process diagnostic report entry: {str(e)}")
            continue

    return clean_reports
