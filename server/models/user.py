from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    device_id: Optional[str] = None
    health_connect: Optional[Dict[str, Any]] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    role: str = "user"
    health_connect_connected: bool = False
    health_connect_token: Optional[str] = None
    health_connect_refresh_token: Optional[str] = None

    class Config:
        from_attributes = True
