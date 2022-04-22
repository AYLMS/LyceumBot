from aiogram.types import Message
from aiogram_dialog import DialogManager

from app import dp
from app.states.register import RegistrationDialog


@dp.message(commands="register", is_registered=False)
async def register_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(RegistrationDialog.greeting)


@dp.message(commands="register", is_registered=True)
async def unregistered_handler(message: Message):
    await message.answer("<b>✅ Вы уже зарегистрированы в боте </b>")
