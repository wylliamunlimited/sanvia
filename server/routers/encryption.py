import sys

# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from constants.url import firebase_rest

from dependencies.firebase_dependencies import (
    get_firebase_user_from_token
)

from constants.credentials import (
    AES_ENCRYPTION_KEY
)

from datetime import datetime, timedelta
router = APIRouter()

@router.get("/get-encryption-key")
async def getEncryptionKey(request: Request, user: Annotated[dict, Depends(get_firebase_user_from_token)]):
    return {"key": AES_ENCRYPTION_KEY}