from aiogram.types import Message
from aiogram_dialog import DialogManager

from app import dp
from app.states.register import RegistrationDialog


@dp.message(commands="register")
async def register_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(RegistrationDialog.greeting)
