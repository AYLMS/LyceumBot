from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_invite_keyboard(url: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🔗 Инвайт для родителя", url=url)
    return keyboard.as_markup()
