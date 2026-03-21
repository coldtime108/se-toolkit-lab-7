import json
import httpx
from typing import Any, Dict, List, Optional


class LLMClient:
    """Client for interacting with LLM with function calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.tools = self._get_tools()

    def _get_tools(self) -> List[Dict]:
        """Define tools (functions) for the LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_labs",
                    "description": "Get list of all available labs",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_scores",
                    "description": "Get pass rates for a specific lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., lab-04"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_learners",
                    "description": "Get count of distinct learners",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_items",
                    "description": "Get all items (labs and tasks)",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_groups",
                    "description": "Get group performance for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., lab-04"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_timeline",
                    "description": "Get submission timeline for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., lab-04"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_completion_rate",
                    "description": "Get completion rate for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., lab-04"}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_top_learners",
                    "description": "Get top learners for a lab",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lab": {"type": "string", "description": "Lab identifier, e.g., lab-04"},
                            "limit": {"type": "integer", "description": "Number of top learners to return", "default": 5}
                        },
                        "required": ["lab"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_health",
                    "description": "Check backend health",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            }
        ]

    async def classify_intent(self, user_input: str, lms_client=None) -> Optional[str]:
        """Classify user intent and return a command string (legacy). For Task 3 we use tools."""
        # We'll use the tool-based approach. This method may be deprecated.
        # But we'll keep for compatibility. For new implementation, we'll call a method that uses tools.
        return None

    async def execute_tool_call(self, tool_name: str, args: dict, lms_client) -> str:
        """Execute a tool call using LMS client and return formatted result."""
        if tool_name == "get_labs":
            items = await lms_client.get("/items/")
            labs = [item["title"] for item in items if item.get("type") == "lab"]
            return "Available labs:\n" + "\n".join(f"- {lab}" for lab in labs)
        elif tool_name == "get_scores":
            lab = args.get("lab")
            if not lab:
                return "Please specify a lab."
            data = await lms_client.get(f"/analytics/pass-rates?lab={lab}")
            lines = []
            for item in data:
                lines.append(f"{item['task']}: {item['avg_score']}% ({item['attempts']} attempts)")
            return f"Scores for {lab}:\n" + "\n".join(lines) if lines else f"No data for {lab}."
        elif tool_name == "get_learners":
            items = await lms_client.get("/learners/")
            return f"Total learners: {len(items)}"
        elif tool_name == "get_items":
            items = await lms_client.get("/items/")
            return f"Total items: {len(items)}"
        elif tool_name == "get_groups":
            lab = args.get("lab")
            if not lab:
                return "Please specify a lab."
            data = await lms_client.get(f"/analytics/groups?lab={lab}")
            lines = []
            for item in data:
                lines.append(f"{item['group']}: avg_score={item['avg_score']}, students={item['students']}")
            return f"Group performance for {lab}:\n" + "\n".join(lines) if lines else f"No group data for {lab}."
        elif tool_name == "get_timeline":
            lab = args.get("lab")
            if not lab:
                return "Please specify a lab."
            data = await lms_client.get(f"/analytics/timeline?lab={lab}")
            lines = []
            for item in data:
                lines.append(f"{item['date']}: {item['submissions']} submissions")
            return f"Submission timeline for {lab}:\n" + "\n".join(lines[:10]) if lines else f"No timeline data for {lab}."
        elif tool_name == "get_completion_rate":
            lab = args.get("lab")
            if not lab:
                return "Please specify a lab."
            data = await lms_client.get(f"/analytics/completion-rate?lab={lab}")
            return f"Completion rate for {lab}: {data.get('completion_rate')}% (passed: {data.get('passed')}, total: {data.get('total')})"
        elif tool_name == "get_top_learners":
            lab = args.get("lab")
            limit = args.get("limit", 5)
            if not lab:
                return "Please specify a lab."
            data = await lms_client.get(f"/analytics/top-learners?lab={lab}&limit={limit}")
            lines = []
            for item in data:
                lines.append(f"Learner {item['learner_id']}: avg_score={item['avg_score']}, attempts={item['attempts']}")
            return f"Top {limit} learners for {lab}:\n" + "\n".join(lines) if lines else f"No learner data for {lab}."
        elif tool_name == "get_health":
            try:
                items = await lms_client.get("/items/")
                return f"Backend is healthy. Items count: {len(items)}"
            except Exception:
                return "Backend is unreachable."
        else:
            return f"Unknown tool: {tool_name}"

    async def answer_with_tools(self, user_input: str, lms_client) -> str:
        """Send user input to LLM, let it decide which tool to call, execute tool, and return answer."""
        messages = [{"role": "user", "content": user_input}]
        # Prepare request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto"
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=body, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            choice = data["choices"][0]
            message = choice["message"]

            if "tool_calls" in message and message["tool_calls"]:
                # Execute the first tool call (for simplicity)
                tool_call = message["tool_calls"][0]
                tool_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])
                result = await self.execute_tool_call(tool_name, args, lms_client)
                # Optionally, we could ask LLM to format result into a nice answer, but for now return raw.
                return result
            else:
                # If no tool call, just return the message content
                return message.get("content", "Sorry, I didn't understand.")
