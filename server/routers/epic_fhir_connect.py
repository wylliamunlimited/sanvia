
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import urllib.parse
import httpx
import json
import base64
from datetime import datetime

from constants.url import (
    EPIC_BASE_URL, SANVIA_BACKEND_BASE_URL, EPIC_TEST_SERVER_URL, FRONTEND_URL
)
from constants.credentials import (
    EPIC_CLIENT_ID
)
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token, update_epic_tokens, get_epic_tokens, get_recent_epic_token
)
from dependencies.epic_dependencies import (
    get_epic_patient_data
)

router = APIRouter()

epic_access_token = dict()


EPIC_TOKEN_API_URL = f"{EPIC_BASE_URL}oauth2/token"
EPIC_AUTH_CODE_API_URL = f"{EPIC_BASE_URL}oauth2/authorize"


@router.get("/auth/epic/callback")
async def fhir_epic_callback(
    request: Request
):
    """Callback endpoint for EPIC to carry out redirect"""
    try:
        auth_code = request.query_params.get("code")
        user_id = request.query_params.get("state")
        
        state_raw = request.query_params.get("state")
        state_decoded = json.loads(base64.urlsafe_b64decode(state_raw.encode()).decode())
        user_id = state_decoded["uid"]
        provider_url = state_decoded["aud"]
        redirect_uri = f"{SANVIA_BACKEND_BASE_URL}/auth/epic/callback"
        
        if not auth_code:
            raise HTTPException(status_code=400, detail=f"Missing authorization code from EPIC.")
        
        params = {
            "code": auth_code,
            "state": user_id,
            "grant_type": "authorization_code",
            "client_id": EPIC_CLIENT_ID,
            "redirect_uri": redirect_uri,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(EPIC_TOKEN_API_URL, data=params, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Token exchange with EPIC failed.")
            
            token_data = response.json()
            
            ## upload to database of the authorization
            # print(f"Saving EPIC tokens for user {user_id}: {token_data.keys()}")
            access_token_cache = update_epic_tokens(user_id=user_id, token_data=token_data)
            epic_access_token.setdefault(user_id, {})[provider_url] = access_token_cache
            
            ## Verify user authentication is successful, by calling an example API call
            ## TODO
            user_data = await get_epic_patient_data(access_token=access_token_cache["access_token"], patient_id=access_token_cache["patient"],
                                              provider_url=provider_url)
            
            print(f"User Data: {user_data}")
            
            
        return RedirectResponse(url=f"{FRONTEND_URL}/profile?provider=EPIC&connect-status=success")
        
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"EPIC FHIR Authorization Pipeline broken."
        )
    
    
@router.get("/auth/epic/redirect")
async def fhir_epic_redirect(
    request: Request,
    user: Annotated[dict, Depends(get_firebase_user_from_token)]
):
    """Redirect function for client to visit EPIC auth"""
    try:
        provider_url = request.query_params.get("provider_url")
        if not provider_url:
            raise HTTPException(status_code=400, detail="Missing provider_url parameter")

        redirect_uri = f"{SANVIA_BACKEND_BASE_URL}/auth/epic/callback"

        state_data = {
            "uid": user["uid"],
            "aud": provider_url
        }

        state_str = base64.urlsafe_b64encode(json.dumps(state_data).encode()).decode()

        params = {
            "response_type": "code",
            "client_id": EPIC_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "state": state_str,
            "scope": "offline_access",
            "aud": provider_url
        }
        
        print(params)

        epic_redirect = EPIC_AUTH_CODE_API_URL + "?" + urllib.parse.urlencode(params)
        
        return {"url": epic_redirect}

    except Exception as e:
        raise HTTPException(status_code=400, detail="EPIC connect unsuccessful.")
    
    