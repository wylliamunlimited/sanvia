from fastapi import APIRouter

router = APIRouter()


# @router.get("/fhir/epic")



# @router.get("/ehr/{patient_id}")
# async def get_ehr_data(patient_id: str):
#     """Fetches patient health data from an EHR system without storing it."""
#     ehr_url = f"https://api.ehrprovider.com/fhir/Patient/{patient_id}"  # Replace with actual API

#     try:
#         response = requests.get(
#             ehr_url, headers={"Authorization": "Bearer YOUR_EHR_ACCESS_TOKEN"}
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.RequestException as e:
#         raise HTTPException(
#             status_code=400, detail=f"Failed to fetch EHR data: {str(e)}"
#         )

