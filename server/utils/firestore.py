from firebase_admin import firestore
from typing import Optional
from ..models.user import User


def get_firestore_client():
    """Get Firestore client instance."""
    return firestore.client()


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user document from Firestore by ID."""
    db = get_firestore_client()
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        return User(**doc.to_dict())
    return None


async def update_user(user_id: str, data: dict) -> None:
    """Update user document in Firestore."""
    db = get_firestore_client()
    db.collection("users").document(user_id).update(data)
