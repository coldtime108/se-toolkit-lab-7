#!/usr/bin/env python3
"""
Telegram Bot for LMS Backend Interaction with Tool Calling

Usage:
    Normal mode:  uv run bot.py
    Test mode:    uv run bot.py --test "/command"

Test mode prints the response to stdout without connecting to Telegram.
"""
import sys
import asyncio
import argparse
from typing import Optional, Dict, Any

from config import load_config
from services.lms_client import LMSClient
from services.llm_client import LLMClient
from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from keyboards import get_main_keyboard, get_labs_keyboard


async def execute_tool(tool_name: str, arguments: Dict[str, Any], lms_client: LMSClient) -> str:
    """Execute a tool and return the result."""
    try:
        if tool_name == "get_health":
            return await handle_health(lms_client)
        
        elif tool_name == "list_labs":
            return await handle_labs(lms_client)
        
        elif tool_name == "get_scores":
            lab_id = arguments.get("lab_id", "")
            return await handle_scores(lab_id, lms_client)
        
        elif tool_name == "get_analytics":
            metric = arguments.get("metric", "pass-rates")
            lab_id = arguments.get("lab_id", "")
            # Call analytics endpoint through LMS client
            result = await lms_client.get_analytics(metric, lab_id)
            if isinstance(result, dict) and "error" in result:
                return f"⚠️ Ошибка: {result['error']}"
            return f"📊 Analytics ({metric}):\n{result}"
        
        elif tool_name == "get_tasks":
            lab_id = arguments.get("lab_id", "")
            tasks = await lms_client.get_tasks(lab_id)
            if not tasks:
                return "⚠️ Задачи не найдены"
            result = f"📋 Задачи для {lab_id}:\n"
            for task in tasks[:10]:
                result += f"• {task.get('title', 'Unknown')}\n"
            return result
        
        elif tool_name == "get_learners":
            group = arguments.get("group", "")
            learners = await lms_client.get_learners(group)
            if not learners:
                return "⚠️ Студенты не найдены"
            return f"👥 Студенты: {len(learners)} чел.\n{learners[:5]}"
        
        elif tool_name == "get_submissions":
            lab_id = arguments.get("lab_id", "")
            limit = arguments.get("limit", 10)
            submissions = await lms_client.get_submissions(lab_id, limit)
            return f"📬 Последняя отправка: {submissions}"
        
        elif tool_name == "get_interactions":
            user_id = arguments.get("user_id", "")
            interactions = await lms_client.get_interactions(user_id)
            return f"🔄 Взаимодействия: {interactions}"
        
        elif tool_name == "sync_data":
            result = await lms_client.sync_data()
            return f"✅ Синхронизация: {result}"
        
        else:
            return f"⚠️ Неизвестный инструмент: {tool_name}"
    
    except Exception as e:
        return f"❌ Ошибка выполнения: {str(e)}"


async def process_with_llm(text: str, lms_client: LMSClient, llm_client: LLMClient) -> str:
    """Process user input using LLM tool calling."""
    # Get tool call from LLM
    tool_call = await llm_client.classify_intent(text)
    
    if tool_call:
        tool_name = tool_call.get("name")
        arguments = tool_call.get("arguments", {})
        
        # Execute the tool
        result = await execute_tool(tool_name, arguments, lms_client)
        return result
    
    # If no tool was called, ask for clarification
    return "⚠️ Я не понял ваш запрос. Попробуйте спросить о лабораторных работах, оценках или статусе системы."


async def process_command(command: str, args: str, lms_client: Optional[LMSClient], llm_client: Optional[LLMClient]) -> str:
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
        return f"⚠️ Неизвестная команда: {command}\n\nИспользуйте /help для списка команд."


async def run_test_mode(command_text: str, config: dict) -> None:
    """Run in test mode - process command and print response."""
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

    command, args = command_text.split(maxsplit=1) if " " in command_text else (command_text, "")
    
    if command.startswith("/"):
        # Command mode
        response = await process_command(command, args, lms_client, llm_client)
    else:
        # Natural language mode with tool calling
        if llm_client:
            response = await process_with_llm(command_text, lms_client, llm_client)
        else:
            response = "⚠️ LLM не настроен. Используйте команды (/start, /help, /health, /labs, /scores)."

    print(response)


async def run_telegram_mode(config: dict) -> None:
    """Run the Telegram bot."""
    from aiogram import Bot, Dispatcher
    from aiogram.filters import Command, CommandStart
    from aiogram.types import Message, CallbackQuery

    if not config.get("bot_token"):
        print("Error: BOT_TOKEN not set. Please configure .env.bot.secret")
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

    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        response = await handle_start(lms_client)
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        response = await handle_help(lms_client)
        await message.answer(response, reply_markup=get_main_keyboard())

    @dp.message(Command("health"))
    async def cmd_health(message: Message):
        response = await handle_health(lms_client)
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: Message):
        response = await handle_labs(lms_client)
        labs = await lms_client.get_labs()
        keyboard = get_labs_keyboard(labs) if labs else None
        await message.answer(response, reply_markup=keyboard)

    @dp.message(Command("scores"))
    async def cmd_scores(message: Message):
        lab_query = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ""
        response = await handle_scores(lab_query, lms_client)
        await message.answer(response)

    @dp.message()
    async def handle_message(message: Message):
        """Handle plain text messages using LLM tool calling."""
        user_text = message.text or ""
        if llm_client:
            response = await process_with_llm(user_text, lms_client, llm_client)
        else:
            response = "⚠️ LLM не настроен. Используйте команды (/start, /help, /health, /labs, /scores)."
        await message.answer(response)

    @dp.callback_query()
    async def handle_callback(callback: CallbackQuery):
        """Handle inline keyboard button clicks."""
        data = callback.data or ""
        
        if data == "cmd_start":
            response = await handle_start(lms_client)
            await callback.message.edit_text(response, reply_markup=get_main_keyboard())
        elif data == "cmd_help":
            response = await handle_help(lms_client)
            await callback.message.edit_text(response, reply_markup=get_main_keyboard())
        elif data == "cmd_health":
            response = await handle_health(lms_client)
            await callback.message.edit_text(response)
        elif data == "cmd_labs":
            response = await handle_labs(lms_client)
            labs = await lms_client.get_labs()
            keyboard = get_labs_keyboard(labs) if labs else None
            await callback.message.edit_text(response, reply_markup=keyboard)
        elif data.startswith("scores_"):
            lab_id = data.replace("scores_", "")
            response = await handle_scores(f"lab-{lab_id}", lms_client)
            await callback.message.edit_text(response)
        
        await callback.answer()

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
