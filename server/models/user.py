from pydantic import BaseModel
from typing import Optional


class User(BaseModel):
    id: str
    email: str
    name: str
    role: str = "user"
    health_connect_connected: bool = False
    health_connect_token: Optional[str] = None
    health_connect_refresh_token: Optional[str] = None
