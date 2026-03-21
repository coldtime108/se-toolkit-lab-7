#!/usr/bin/env python3
"""
Telegram Bot for LMS Backend Interaction

Usage:
    Normal mode:  uv run bot.py
    Test mode:    uv run bot.py --test "/command"

Test mode prints the response to stdout without connecting to Telegram.
"""
import sys
import asyncio
import argparse
from typing import Optional

from config import load_config
from services import LMSClient, LLMClient
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command text into command and arguments."""
    text = text.strip()
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        return command, args
    return "", text


async def process_command(command: str, args: str, lms_client: LMSClient, llm_client: Optional[LLMClient]) -> str:
    """Process a command and return the response."""
    if command == "/start":
        return await handle_start(lms_client)
    elif command == "/help":
        return await handle_help(lms_client)
    elif command == "/health":
        return await handle_health(lms_client)
    elif command == "/labs":
        return await handle_labs(lms_client)
    elif command == "/scores":
        return await handle_scores(args, lms_client)
    else:
        # Try to use LLM for intent classification
        if llm_client:
            classified = await llm_client.classify_intent(f"{command} {args}".strip())
            if classified:
                return await process_command(classified, "", lms_client, llm_client)
        return f"⚠️ Неизвестная команда: {command}\n\nИспользуйте /help для списка команд."


async def run_test_mode(command_text: str, config: dict) -> None:
    """Run in test mode - process command and print response."""
    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )
    
    llm_client = None
    if config["llm_api_key"]:
        llm_client = LLMClient(
            api_key=config["llm_api_key"],
            base_url=config["llm_api_base_url"],
            model=config["llm_api_model"]
        )
    
    command, args = parse_command(command_text)
    
    # If no command detected, use LLM to classify
    if not command and llm_client:
        classified = await llm_client.classify_intent(command_text)
        if classified:
            command, args = parse_command(classified)
    
    if command:
        response = await process_command(command, args, lms_client, llm_client)
    else:
        response = "⚠️ Не удалось распознать команду. Используйте /help для списка команд."
    
    print(response)


async def run_telegram_mode(config: dict) -> None:
    """Run the Telegram bot."""
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command, CommandStart
    from aiogram.types import Message
    
    if not config["bot_token"]:
        print("Error: BOT_TOKEN not set. Please configure .env.bot.secret")
        sys.exit(1)
    
    bot = Bot(token=config["bot_token"])
    dp = Dispatcher()
    
    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )
    
    llm_client = None
    if config["llm_api_key"]:
        llm_client = LLMClient(
            api_key=config["llm_api_key"],
            base_url=config["llm_api_base_url"],
            model=config["llm_api_model"]
        )
    
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        response = await handle_start(lms_client)
        await message.answer(response)
    
    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        response = await handle_help(lms_client)
        await message.answer(response)
    
    @dp.message(Command("health"))
    async def cmd_health(message: Message):
        response = await handle_health(lms_client)
        await message.answer(response)
    
    @dp.message(Command("labs"))
    async def cmd_labs(message: Message):
        response = await handle_labs(lms_client)
        await message.answer(response)
    
    @dp.message(Command("scores"))
    async def cmd_scores(message: Message):
        lab_query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = await handle_scores(lab_query, lms_client)
        await message.answer(response)
    
    @dp.message()
    async def handle_message(message: Message):
        """Handle plain text messages using LLM for intent routing."""
        if not llm_client:
            await message.answer("⚠️ LLM не настроен. Используйте команды (/start, /help, /health, /labs, /scores).")
            return
        
        user_text = message.text or ""
        classified = await llm_client.classify_intent(user_text)
        
        if classified:
            command, args = parse_command(classified)
            response = await process_command(command, args, lms_client, llm_client)
        else:
            response = "⚠️ Я не понял ваш запрос. Попробуйте использовать команды (/help для списка)."
        
        await message.answer(response)
    
    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Test mode: process command and print response (e.g., --test '/start')"
    )
    args = parser.parse_args()
    
    config = load_config()
    
    if args.test:
        # Test mode
        asyncio.run(run_test_mode(args.test, config))
    else:
        # Normal Telegram bot mode
        asyncio.run(run_telegram_mode(config))


if __name__ == "__main__":
    main()
