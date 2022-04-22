from aiogram.types import Message

from app import dp
from app.common import FMT


@dp.message(is_registered=False)
async def unregistered_handler(message: Message, f: FMT):
    await message.answer(
        "<b> ⚠️ Для использования этой команды вам необходимо зарегистрироваться с помощью команды</b> /register"
    )
