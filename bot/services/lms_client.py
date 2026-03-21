"""
LMS API Client service.
Handles all communication with the LMS backend.
"""
import httpx
from typing import Optional, List, Dict, Any


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
                    return [item for item in items if item.get("type") == "lab"]
                return []
        except Exception:
            return []

    async def get_scores(self, lab_id: str) -> dict:
        """Get scores/pass rates for a specific lab."""
        try:
            # Extract numeric ID from lab_id string like "lab-01"
            numeric_id = lab_id.replace("lab-", "").replace("lab_", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/analytics/tasks/?lab_id={numeric_id}",
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

    async def get_analytics(self, metric: str, lab_id: str = "") -> dict:
        """Get analytics data (pass-rates, score-distribution, etc.)."""
        try:
            async with httpx.AsyncClient() as client:
                if lab_id:
                    numeric_id = lab_id.replace("lab-", "").replace("lab_", "")
                    url = f"{self.base_url}/analytics/tasks/?lab_id={numeric_id}"
                else:
                    url = f"{self.base_url}/analytics/{metric}/"
                
                response = await client.get(url, headers=self._headers, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_tasks(self, lab_id: str) -> list:
        """Get tasks for a specific lab."""
        try:
            numeric_id = lab_id.replace("lab-", "").replace("lab_", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers,
                    timeout=10.0
                )
                if response.status_code == 200:
                    all_items = response.json()
                    # Filter tasks for this lab
                    return [item for item in all_items if item.get("parent_id") == int(numeric_id)]
                return []
        except Exception:
            return []

    async def get_learners(self, group: str = "") -> list:
        """Get list of learners/students."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/learners/"
                if group:
                    url += f"?group={group}"
                response = await client.get(url, headers=self._headers, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception:
            return []

    async def get_submissions(self, lab_id: str = "", limit: int = 10) -> list:
        """Get submission statistics."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/analytics/submissions/"
                if lab_id:
                    numeric_id = lab_id.replace("lab-", "").replace("lab_", "")
                    url += f"?lab_id={numeric_id}"
                response = await client.get(url, headers=self._headers, timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    return data[:limit] if isinstance(data, list) else data
                return []
        except Exception:
            return []

    async def get_interactions(self, user_id: str = "") -> dict:
        """Get interaction data."""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/interactions/"
                if user_id:
                    url += f"?user_id={user_id}"
                response = await client.get(url, headers=self._headers, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def sync_data(self) -> dict:
        """Trigger ETL pipeline sync."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pipeline/sync",
                    headers=self._headers,
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Status: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
