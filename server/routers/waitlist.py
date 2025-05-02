import sys

sys.path.insert(1, "../dependencies")
sys.path.insert(2, "../constants")

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from dependencies.firebase_dependencies import get_firestore_client
from datetime import datetime

router = APIRouter()

class WaitlistEntry(BaseModel):
    email: str
    age: Optional[int] = None
    role: Optional[str] = None

@router.post("/waitlist/submit")
async def submit_waitlist(entry: WaitlistEntry):
    """Submit a new entry to the waitlist."""
    try:
        # Get Firestore client
        db = get_firestore_client()
        
        # Create a new document in the waitlist collection
        waitlist_ref = db.collection("waitlist")
        
        # Add the entry with timestamp
        waitlist_ref.add({
            "email": entry.email,
            "age": entry.age,
            "role": entry.role,
            "submitted_at": datetime.utcnow(),
            "status": "pending"
        })
        
        return {"message": "Successfully added to waitlist"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit to waitlist: {str(e)}"
        ) 