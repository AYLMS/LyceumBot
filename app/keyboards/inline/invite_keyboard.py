from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import owner_id


def get_invite_keyboard(url: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔗 Инвайт для родителя", url=url)
    return keyboard.as_markup()
