"""
LLM Client service for intent routing with Tool Calling.
Uses OpenAI-compatible function calling API.
"""
import httpx
import json
from typing import Optional, List, Dict, Any, Callable


# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_health",
            "description": "Check if the LMS backend is healthy and operational",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_labs",
            "description": "List all available laboratory works in the LMS",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_scores",
            "description": "Get scores and pass rates for a specific laboratory work",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {
                        "type": "string",
                        "description": "The laboratory work ID (e.g., 'lab-01', 'lab-04')"
                    }
                },
                "required": ["lab_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_analytics",
            "description": "Get analytics data including pass rates, score distribution, and group performance",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric": {
                        "type": "string",
                        "description": "The analytics metric to retrieve (e.g., 'pass-rates', 'score-distribution', 'timeline')"
                    },
                    "lab_id": {
                        "type": "string",
                        "description": "Optional laboratory work ID to filter analytics"
                    }
                },
                "required": ["metric"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks",
            "description": "Get tasks for a specific laboratory work",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {
                        "type": "string",
                        "description": "The laboratory work ID to get tasks for"
                    }
                },
                "required": ["lab_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learners",
            "description": "Get list of learners/students enrolled in the course",
            "parameters": {
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "Optional group identifier to filter learners"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_submissions",
            "description": "Get submission statistics and timeline",
            "parameters": {
                "type": "object",
                "properties": {
                    "lab_id": {
                        "type": "string",
                        "description": "Laboratory work ID to get submissions for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of submissions to return"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_interactions",
            "description": "Get interaction data between students and the system",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Optional user ID to filter interactions"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sync_data",
            "description": "Trigger ETL pipeline to sync data from autochecker API",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


class LLMClient:
    """Client for interacting with the LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.tools = TOOLS

    async def chat_with_tools(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> Dict[str, Any]:
        """
        Send a chat request with tool calling support.
        Returns the full response including potential tool calls.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "tools": self.tools,
                        "tool_choice": "auto",
                        "temperature": temperature
                    },
                    timeout=30.0
                )
                if response.status_code == 200:
                    return response.json()
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Send a simple chat request without tools."""
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

    def extract_tool_call(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract tool call information from LLM response.
        Returns dict with 'name' and 'arguments' if a tool was called.
        """
        try:
            choices = response.get("choices", [])
            if not choices:
                return None
            
            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                tool_call = tool_calls[0]
                function = tool_call.get("function", {})
                return {
                    "name": function.get("name"),
                    "arguments": json.loads(function.get("arguments", "{}"))
                }
            return None
        except Exception:
            return None

    async def classify_intent(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Classify user intent and return the appropriate tool call.
        Returns dict with 'name' and 'arguments' for the tool to call.
        """
        prompt = f"""You are a helpful assistant for a Learning Management System (LMS).
Analyze the user's request and call the appropriate tool to help them.

Available tools:
- get_health: Check if backend is working
- list_labs: Show all available labs
- get_scores: Get scores for a specific lab (requires lab_id)
- get_analytics: Get analytics data (pass-rates, score-distribution, etc.)
- get_tasks: Get tasks for a lab
- get_learners: Get list of students
- get_submissions: Get submission statistics
- get_interactions: Get interaction data
- sync_data: Trigger data sync

User request: "{user_message}"

Call the appropriate tool with the right parameters."""

        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_with_tools(messages)
        
        tool_call = self.extract_tool_call(response)
        if tool_call:
            return tool_call
        
        # If no tool was called, return None (unclear request)
        return None

    async def extract_lab_number(self, user_message: str) -> Optional[str]:
        """Extract lab number from user message using LLM."""
        prompt = f"""Extract the lab number from this message.
Respond with ONLY the lab ID in format "lab-XX" (e.g., "lab-01", "lab-04").
If no lab is mentioned, respond with "none".

Message: "{user_message}"

Lab ID:"""

        messages = [{"role": "user", "content": prompt}]
        result = await self.chat(messages)
        
        if result and result.strip().lower() != "none":
            return result.strip()
        return None
