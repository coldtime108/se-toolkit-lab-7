"""
LMS API Client service.
Handles all communication with the LMS backend.
"""
import httpx
from typing import Any, List, Dict


class LMSClient:
    """Client for interacting with the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def get(self, path: str) -> Any:
        """Perform a GET request to the given path."""
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers, timeout=10.0)
            resp.raise_for_status()
            return resp.json()

    async def health_check(self) -> Dict:
        """Check backend health."""
        try:
            items = await self.get("/items/")
            return {"status": "up", "items_count": len(items)}
        except Exception as e:
            return {"status": "down", "error": str(e)}

    async def get_labs(self) -> List[Dict]:
        """Get all labs."""
        items = await self.get("/items/")
        return [item for item in items if item.get("type") == "lab"]

    async def get_items(self) -> List[Dict]:
        """Get all items."""
        return await self.get("/items/")
