#!/usr/bin/env python3
import sys
import asyncio
import argparse
from typing import Optional

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    handle_unknown
)

from config import load_config
from services.lms_client import LMSClient
from services.llm_client import LLMClient


def parse_command(text: str) -> tuple:
    text = text.strip()
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        return command, args
    return "", text


async def process_command(command: str, args: str, lms_client: Optional[LMSClient], llm_client: Optional[LLMClient]) -> str:
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
        return f"⚠️ Неизвестная команда: {command}\n\nИспользуйте /help для списка команд."


async def run_test_mode(command_text: str, config: dict) -> None:
    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )

    llm_client = None
    if config.get("llm_api_key") and config.get("llm_api_base_url"):
        try:
            llm_client = LLMClient(
                api_key=config["llm_api_key"],
                base_url=config["llm_api_base_url"],
                model=config.get("llm_api_model", "coder-model")
            )
        except Exception:
            llm_client = None

    command, args = parse_command(command_text)
    if command:
        response = await process_command(command, args, lms_client, llm_client)
    else:
        if llm_client:
            response = await llm_client.answer_with_tools(command_text, lms_client)
        else:
            response = "⚠️ LLM not configured. Use slash commands."
    print(response)


async def run_telegram_mode(config: dict) -> None:
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command, CommandStart
    from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.types import BotCommand, BotCommandScopeDefault

    if not config.get("bot_token"):
        print("Error: BOT_TOKEN not set.")
        sys.exit(1)

    bot = Bot(token=config["bot_token"])
    dp = Dispatcher()

    lms_client = LMSClient(
        base_url=config["lms_api_url"],
        api_key=config["lms_api_key"]
    )

    llm_client = None
    if config.get("llm_api_key") and config.get("llm_api_base_url"):
        try:
            llm_client = LLMClient(
                api_key=config["llm_api_key"],
                base_url=config["llm_api_base_url"],
                model=config.get("llm_api_model", "coder-model")
            )
        except Exception:
            llm_client = None

    # Set bot commands menu
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="help", description="Show help"),
        BotCommand(command="health", description="Check backend health"),
        BotCommand(command="labs", description="List all labs"),
        BotCommand(command="scores", description="Get scores for a lab (e.g., /scores lab-04)"),
    ], scope=BotCommandScopeDefault())

    def main_keyboard():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Labs", callback_data="labs"),
             InlineKeyboardButton(text="📊 Scores", callback_data="scores")],
            [InlineKeyboardButton(text="🏥 Health", callback_data="health"),
             InlineKeyboardButton(text="❓ Help", callback_data="help")]
        ])

    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        text = await handle_start(lms_client)
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        text = await handle_help(lms_client)
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: Message):
        text = await handle_health(lms_client)
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message):
        text = await handle_labs(lms_client)
        await message.answer(text, reply_markup=main_keyboard())

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message):
        parts = message.text.split(maxsplit=1)
        lab = parts[1] if len(parts) > 1 else ""
        text = await handle_scores(lab, lms_client)
        await message.answer(text, reply_markup=main_keyboard())

    @dp.callback_query()
    async def handle_callback(callback_query):
        data = callback_query.data
        if data == "labs":
            text = await handle_labs(lms_client)
        elif data == "scores":
            text = "Please send /scores <lab> (e.g., /scores lab-04)"
        elif data == "health":
            text = await handle_health(lms_client)
        elif data == "help":
            text = await handle_help(lms_client)
        else:
            text = "Unknown command"
        await callback_query.message.answer(text, reply_markup=main_keyboard())
        await callback_query.answer()

    @dp.message()
    async def handle_message(message: Message):
        user_text = message.text or ""
        if not llm_client:
            await message.answer("⚠️ LLM not configured. Use slash commands.", reply_markup=main_keyboard())
            return

        try:
            response = await llm_client.answer_with_tools(user_text, lms_client)
            await message.answer(response, reply_markup=main_keyboard())
        except Exception as e:
            await message.answer(f"❌ Error: {e}", reply_markup=main_keyboard())

    print("Bot is running... Press Ctrl+C to stop.")
    await dp.start_polling(bot)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument("--test", type=str, metavar="COMMAND", help="Test mode: process command and print response")
    args = parser.parse_args()

    config = load_config()

    if args.test:
        try:
            asyncio.run(run_test_mode(args.test, config))
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        asyncio.run(run_telegram_mode(config))


if __name__ == "__main__":
    main()
