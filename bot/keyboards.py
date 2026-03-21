"""
Inline keyboard layouts for the Telegram bot.
Provides quick action buttons for common commands.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get the main keyboard with common actions."""
    keyboard: List[List[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(text="👋 Start", callback_data="cmd_start"),
            InlineKeyboardButton(text="❓ Help", callback_data="cmd_help"),
        ],
        [
            InlineKeyboardButton(text="💚 Health", callback_data="cmd_health"),
            InlineKeyboardButton(text="📋 Labs", callback_data="cmd_labs"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_labs_keyboard(labs: List[dict]) -> InlineKeyboardMarkup:
    """Get keyboard with lab buttons."""
    keyboard: List[List[InlineKeyboardButton]] = []
    
    # Group labs in pairs for better layout
    row: List[InlineKeyboardButton] = []
    for lab in labs[:10]:  # Limit to 10 labs to avoid huge keyboard
        lab_id = lab.get("id", "?")
        title = lab.get("title", f"Lab {lab_id}")
        # Shorten title for button
        short_title = title.replace("Lab 0", "Lab ").replace("Lab ", "L")[:20]
        row.append(InlineKeyboardButton(text=short_title, callback_data=f"scores_{lab_id}"))
        
        if len(row) == 2:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_scores_keyboard(lab_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for scores navigation."""
    keyboard: List[List[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="📋 Все лабы", callback_data="cmd_labs")],
        [InlineKeyboardButton(text="🔄 Обновить", callback_data=f"scores_{lab_id}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
