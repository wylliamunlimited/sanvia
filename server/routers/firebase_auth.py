import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
import requests
from firebase_admin import auth
from dependencies.firebase_dependencies import (
    get_firebase_user_from_token,
    update_survey_entry,
    get_firestore_client,
)


router = APIRouter()


@router.get("/userid")
async def get_userid(user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    """Gets the Firebase authenticated user ID."""
    return {"id": user["uid"], "email": user.get("email", "No email found")}
