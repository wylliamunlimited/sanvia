from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        # Verify the Firebase token
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]

        # Get user data from Firestore
        from dependencies.firebase_dependencies import get_firestore_client

        db = get_firestore_client()
        user_doc = db.collection("users").document(uid).get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_data = user_doc.to_dict()
        return User(
            id=uid,
            email=user_data.get("email"),
            name=user_data.get("name"),
            role=user_data.get("role", "user"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
