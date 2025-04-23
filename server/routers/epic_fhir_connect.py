
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import urllib.parse
import httpx
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
        
        if not auth_code:
            raise HTTPException(status_code=400, detail=f"Missing authorization code from EPIC.")
        
        params = {
            "code": auth_code,
            "state": user_id,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(EPIC_TOKEN_API_URL, data=params, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Token exchange with WHOOP failed.")
            
            token_data = response.json()
            
            ## upload to database of the authorization
            # print(f"Saving WHOOP tokens for user {user_id}: {token_data.keys()}")
            access_token_cache = update_epic_tokens(user_id=user_id, token_data=token_data)
            epic_access_token[user_id] = access_token_cache
            
            ## Verify user authentication is successful, by calling an example API call
            ## TODO
            
        return RedirectResponse(url=f"{FRONTEND_URL}/profile?provider=whoop&connect-status=success")
        
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

        params = {
            "response_type": "code",
            "client_id": EPIC_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "state": user['uid'],
            "scope": "offline_access",
            "aud": provider_url
        }
        
        # print(params)

        epic_redirect = EPIC_AUTH_CODE_API_URL + "?" + urllib.parse.urlencode(params)
        
        return {"url": epic_redirect}

    except Exception as e:
        raise HTTPException(status_code=400, detail="EPIC connect unsuccessful.")
    
    