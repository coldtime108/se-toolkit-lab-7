"""
Command handlers for the Telegram bot.
These handlers are pure functions - they don't know about Telegram.
This makes them testable without the Telegram API.
"""
from typing import Optional
from ..services.lms_client import LMSClient


async def handle_start(lms_client: Optional[LMSClient] = None) -> str:
    """Handle /start command - welcome message."""
    return (
        "👋 Добро пожаловать в LMS Bot!\n\n"
        "Я ваш помощник для взаимодействия с системой управления обучением.\n"
        "Используйте /help, чтобы увидеть список доступных команд."
    )


async def handle_help(lms_client: Optional[LMSClient] = None) -> str:
    """Handle /help command - list available commands."""
    return (
        "📚 Доступные команды:\n\n"
        "/start - Приветственное сообщение\n"
        "/help - Показать эту справку\n"
        "/health - Проверить статус бэкенда\n"
        "/labs - Показать доступные лабораторные работы\n"
        "/scores <lab> - Показать результаты по лабораторной\n\n"
        "Вы также можете писать обычные сообщения, и я постараюсь понять, что вам нужно!"
    )


async def handle_health(lms_client: LMSClient) -> str:
    """Handle /health command - check backend status."""
    if not lms_client:
        return "⚠️ LMS клиент не настроен"
    
    result = await lms_client.health_check()
    status = result.get("status", "unknown")
    
    if status == "up":
        return "✅ Бэкенд работает нормально\n\n" + str(result.get("data", {}))
    elif status == "degraded":
        return "⚠️ Бэкенд работает с проблемами\n\n" + result.get("error", "")
    else:
        return "❌ Бэкенд недоступен\n\n" + result.get("error", "Неизвестная ошибка")


async def handle_labs(lms_client: LMSClient) -> str:
    """Handle /labs command - list available labs."""
    if not lms_client:
        return "⚠️ LMS клиент не настроен"
    
    labs = await lms_client.get_labs()
    
    if not labs:
        return "⚠️ Не удалось получить список лабораторных работ"
    
    result = "📋 Доступные лабораторные работы:\n\n"
    for lab in labs:
        lab_id = lab.get("id", "?")
        title = lab.get("title", "Без названия")
        result += f"• Lab {lab_id}: {title}\n"
    
    return result


async def handle_scores(lab_query: str, lms_client: LMSClient) -> str:
    """Handle /scores command - get scores for a lab."""
    if not lms_client:
        return "⚠️ LMS клиент не настроен"
    
    if not lab_query:
        return "⚠️ Пожалуйста, укажите номер лабораторной работы\n\nПример: /scores lab-01"
    
    # Try to find the lab by title or ID
    labs = await lms_client.get_labs()
    target_lab = None
    
    # Search by ID or title
    lab_query_lower = lab_query.lower()
    for lab in labs:
        lab_id = str(lab.get("id", ""))
        title = lab.get("title", "").lower()
        if lab_query_lower in title or lab_query_lower == lab_id:
            target_lab = lab
            break
    
    if not target_lab:
        return f"❌ Лабораторная работа \"{lab_query}\" не найдена\n\nИспользуйте /labs, чтобы увидеть доступные работы."
    
    lab_id = target_lab.get("id")
    lab_title = target_lab.get("title")
    
    # Get scores/analytics
    scores = await lms_client.get_scores(lab_id)
    
    if "error" in scores:
        return f"⚠️ Не удалось получить данные по {lab_title}\n\nОшибка: {scores['error']}"
    
    result = f"📊 Результаты по {lab_title}:\n\n"
    
    # Format the scores data
    if isinstance(scores, list):
        for task in scores:
            task_title = task.get("title", "Unknown")
            # Add task stats if available
            result += f"• {task_title}\n"
    elif isinstance(scores, dict):
        for key, value in scores.items():
            result += f"• {key}: {value}\n"
    else:
        result += "Данные получены, но формат не распознан."
    
    return result
