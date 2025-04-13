import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

import httpx
import json
from typing import Annotated
from constants.credentials import (
    WHOOP_CLIENT_ID, WHOOP_CLIENT_SECRET
)
from constants.url import (
    WHOOP_BASE_URL, FRONTEND_URL
)
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_whoop_tokens, get_whoop_tokens, get_recent_whoop_token
)
from dependencies.whoop_dependencies import (
    get_whoop_sleep, get_whoop_user
)
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import urllib.parse
from datetime import datetime


## URLs
WHOOP_OAUTH_URL = WHOOP_BASE_URL + "oauth/oauth2/"
WHOOP_AUTH_CODE_API_URL = WHOOP_OAUTH_URL + "auth"
WHOOP_TOKEN_API_URL = WHOOP_OAUTH_URL + "token"

SCOPES = "offline read:recovery read:cycles read:sleep read:workout read:profile read:body_measurement" ## Access Scope


router = APIRouter()

base_url = f"https://oauth-dev.sanvia.app"

whoop_access_token = dict()

def check_access_token(user_id: str) -> dict:
    """Check if access token is valid"""
    
    token_info = whoop_access_token.get(user_id)
    
    if not token_info:
        return {"status": "Missing"}
    
    if datetime.utcnow() >= token_info["expiration_date"]:
        return {"status": "Expired"}
    
    return {
        "status": "Valid",
        "access_token": token_info["access_token"]
    }

async def get_valid_whoop_token(user_id: str):
    status = check_access_token(user_id)
    if status["status"] == "Valid":
        return status["access_token"]
    elif status["status"] == "Expired":
        return await refresh_token(user_id)
    else:
        raise HTTPException(status_code=401, detail="WHOOP token not found.")

## Implement Token Refreshing 
##      All refreshes have to be done before the token expires
##      Need a way to do this regularly (Need ChatGPT's help)
async def refresh_token(user_id: str):
    """Refresh token set for user."""
    
    token_data = get_recent_whoop_token(user_id=user_id)

    refresh_token = token_data["refresh_token"]
    
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "scope": "offline",
        "client_id": WHOOP_CLIENT_ID,
        "client_secret": WHOOP_CLIENT_SECRET,
    }
    
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        res = await client.post(WHOOP_TOKEN_API_URL, data=params, headers=headers)

    if res.status_code != 200:
        try:
            err = res.json()
            if err.get("error") == "invalid_grant":
                print(f"Refresh token expired for user {user_id}. Clearing token...")
                whoop_access_token.pop(user_id, None)
                raise HTTPException(status_code=401, detail="Refresh token expired or revoked. Please reconnect WHOOP.")
        except Exception:
            pass

        raise HTTPException(status_code=500, detail="WHOOP token refresh failed")

    new_token_data = res.json()
            # access_token: string
            # refresh_token: string
            # expires_in: number
            # scope: string
            # token_type: 'bearer'

    new_cache_data = update_whoop_tokens(user_id=user_id, token_data=new_token_data)

    # Update in-memory cache
    whoop_access_token[user_id] = {
        "access_token": new_cache_data["access_token"],
        "expiration_date": new_cache_data["expiration_date"]
    }
    
    ## Verify user authentication is successful 
    user_data = await get_whoop_user(access_token=whoop_access_token[user_id]["access_token"])
    print(json.dumps(user_data, indent=4))

    return new_cache_data["access_token"]


@router.get("/auth/whoop/callback", name="whoop_callback")
async def whoop_callback(request: Request):
    """[WHOOP] This endpoint receives WHOOP request after user signs in"""
    ### Receiving Authorization Code
    try:
        auth_code = request.query_params.get("code")
        user_id = request.query_params.get("state")
        
        if not auth_code:
            raise HTTPException(status_code=400, detail=f"Missing authorization code from WHOOP.")
        
        redirectURI = f"{base_url}/auth/whoop/callback"
        
        params = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirectURI,
            "client_id": WHOOP_CLIENT_ID,
            "client_secret": WHOOP_CLIENT_SECRET,
            "scope": "offline"
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(WHOOP_TOKEN_API_URL, data=params, headers=headers)
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Token exchange with WHOOP failed.")
            
            token_data = response.json()
            
            ## upload to database of the authorization
            # print(f"Saving WHOOP tokens for user {user_id}: {token_data.keys()}")
            access_token_cache = update_whoop_tokens(user_id=user_id, token_data=token_data)
            whoop_access_token[user_id] = access_token_cache
            
            ## Verify user authentication is successful 
            user_data = await get_whoop_user(access_token=whoop_access_token[user_id]["access_token"])
            print(json.dumps(user_data, indent=4))
            
        return RedirectResponse(url=f"{FRONTEND_URL}/profile")
    except Exception as e:
        print(f"Whoop Callback Error: {e}")
        raise HTTPException(status_code=400, detail=f"Whoop Callback Failed. {e}")
    
    
    
@router.get("/auth/whoop/redirect", name="whoop_redirect")
async def whoop_redirect(request: Request, user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """[WHOOP] This endpoint redirects user to WHOOP sign in page."""
    try:
        redirectURI = f"{base_url}/auth/whoop/callback"
        
        params = {
            "client_id": WHOOP_CLIENT_ID,
            "redirect_uri": redirectURI,
            "response_type": "code",
            "scope": SCOPES,
            "state": user["uid"]
        }
        
        whoop_redirect = WHOOP_AUTH_CODE_API_URL + "?" + urllib.parse.urlencode(params)
        return {"url": whoop_redirect}
    except:
        raise HTTPException(status_code=500, detail=f"WHOOP Redirect Unreachable. Error on Sanvia Server...")
    

@router.get("/auth/whoop/refresh")
async def manual_refresh(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    try:
        new_token = await refresh_token(user["uid"])
        return {"status": "success", "access_token": new_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to refresh token: {e}")
    
    
# + ---------------------- +
# |     Data Operations    |
# + ---------------------- +
@router.get("/data/whoop/sleep")
async def get_whoop_sleep(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    ...