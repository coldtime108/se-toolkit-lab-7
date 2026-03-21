"""
LLM Client service for intent routing.
Handles communication with the LLM API.
"""
import httpx
from typing import Optional, List, Dict, Any


class LLMClient:
    """Client for interacting with the LLM API."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Send a chat request to the LLM and get a response."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": messages
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content")
                return None
        except Exception:
            return None
    
    async def classify_intent(self, user_message: str) -> Optional[str]:
        """Classify user intent and return the appropriate command."""
        prompt = f"""You are a Telegram bot assistant for an LMS (Learning Management System).
Classify the user's message into one of these commands:
- /start - Welcome message
- /help - List available commands
- /health - Check backend status
- /labs - List available labs
- /scores - Get scores for a lab (user should specify lab name/number)

User message: "{user_message}"

Respond with ONLY the command (e.g., "/labs" or "/scores lab-04"). If unclear, respond with "/help"."""
        
        messages = [{"role": "user", "content": prompt}]
        return await self.chat(messages)
