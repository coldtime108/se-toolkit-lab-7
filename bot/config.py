"""
Configuration module for the Telegram bot.
Loads environment variables from .env.bot.secret or .env.bot.example.
"""
import os
from dotenv import load_dotenv
from pathlib import Path


def get_base_dir() -> Path:
    """Get the base directory of the bot."""
    return Path(__file__).parent


def load_config() -> dict:
    """Load configuration from environment variables."""
    base_dir = get_base_dir()
    
    # Try to load from .env.bot.secret first, then .env.bot.example
    secret_env = base_dir / ".env.bot.secret"
    example_env = base_dir / ".env.bot.example"
    
    if secret_env.exists():
        load_dotenv(secret_env)
    elif example_env.exists():
        load_dotenv(example_env)
    
    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_url": os.getenv("LMS_API_URL", "http://localhost:42002"),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        "llm_api_model": os.getenv("LLM_API_MODEL", "coder-model"),
    }
