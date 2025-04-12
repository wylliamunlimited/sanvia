import httpx
from typing import Optional, Dict, Any
from ..models.user import User


class HealthConnectClient:
    def __init__(self, base_url: str = "https://api.healthconnect.com/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def get_user_data(self, user: User) -> Optional[Dict[str, Any]]:
        """Get user's health data from Health Connect."""
        if not user.health_connect_token:
            return None

        headers = {
            "Authorization": f"Bearer {user.health_connect_token}",
            "Content-Type": "application/json",
        }

        try:
            response = await self.client.get(
                f"{self.base_url}/user/data", headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError:
            return None

    async def refresh_token(self, user: User) -> bool:
        """Refresh Health Connect access token."""
        if not user.health_connect_refresh_token:
            return False

        try:
            response = await self.client.post(
                f"{self.base_url}/oauth/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": user.health_connect_refresh_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            # Update user's tokens
            user.health_connect_token = data["access_token"]
            user.health_connect_refresh_token = data["refresh_token"]
            return True
        except httpx.HTTPError:
            return False
