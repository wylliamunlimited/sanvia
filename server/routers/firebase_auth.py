import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from firebase_admin import auth
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token
)
from constants.url import firebase_rest
from constants.credentials import FIREBASE_ADMIN_API_KEY

from pydantic import BaseModel

class SignInRequest(BaseModel):
    email: str
    password: str
    returnSecureToken: bool = True
    
    
class SignUpRequest(BaseModel):
    email: str
    password: str
    returnSecureToken: bool = True
    firstname: str
    lastname: str
    

router = APIRouter()


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the Firebase authenticated user ID."""
    return {"id": user["uid"], "email": user.get("email", "No email found")}


@router.post("/signin")
async def sign_in(request: SignInRequest):
    """
    Description
    -----------
    Sign in with Firebase.
    
    Parameters
    ----------
    request: SignInRequest
        The request body containing email and password.
        
    Returns
    -------
    dict
        The response from Firebase:
            {
                "localId": "ZY1rJK0eYLg...",
                "email": "[user@example.com]",
                "displayName": "",
                "idToken": "[ID_TOKEN]",
                "registered": true,
                "refreshToken": "[REFRESH_TOKEN]",
                "expiresIn": "3600"
            }
    """
    
    url = firebase_rest("signInWithPassword")
    
    header = {'Content-Type': 'application/json'}
    
    payload = {
        "email": request.email,
        "password": request.password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload, headers=header)
    
    if response.status_code != 200:
        print(f"❌ Error signing in: {response.json()}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    else:
        return {"details": response.json()}


@router.get("/signout")
async def sign_out():
    pass

@router.post("/signup")
async def sign_up(request: SignUpRequest):
    """
    Description
    -----------
    Sign up with Firebase.
    
    Parameters
    ----------
    request: SignUpRequest
        The request body containing 
            - email
            - password
            - first name
            - last name
            - returnSecureToken
        
    Returns
    -------
    dict
        The response from Firebase:
            {
                "idToken": "[ID_TOKEN]",
                "email": "[user@example.com]",
                "refreshToken": "[REFRESH_TOKEN]",
                "expiresIn": "3600",
                "localId": "tRcfmLH7..."
            }
    """
    
    url = firebase_rest("signUp")
    
    header = {'Content-Type': 'application/json'}
    
    payload = {
        "email": request.email,
        "password": request.password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload, headers=header)
    
    if response.status_code != 200:
        print(f"❌ Error signing in: {response.json()}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    else:
        return {"details": response.json()}
