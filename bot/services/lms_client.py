"""
LMS API Client service.
Handles all communication with the LMS backend.
"""
import httpx
from typing import Optional


class LMSClient:
    """Client for interacting with the LMS backend API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}
    
    async def health_check(self) -> dict:
        """Check if the backend is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self._headers,
                    timeout=5.0
                )
                if response.status_code == 200:
                    return {"status": "up", "data": response.json()}
                return {"status": "degraded", "error": f"Status: {response.status_code}"}
        except httpx.ConnectError:
            return {"status": "down", "error": "Backend is not reachable"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
    
    async def get_labs(self) -> list:
        """Get all available labs."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    items = response.json()
                    # Filter only lab items (type == "lab")
                    return [item for item in items if item.get("type") == "lab"]
                return []
        except Exception:
            return []
    
    async def get_scores(self, lab_id: int) -> dict:
        """Get scores/pass rates for a specific lab."""
        try:
            async with httpx.AsyncClient() as client:
                # Get analytics for the lab
                response = await client.get(
                    f"{self.base_url}/analytics/tasks/?lab_id={lab_id}",
                    headers=self._headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_items(self) -> list:
        """Get all items (labs and tasks)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception:
            return []
