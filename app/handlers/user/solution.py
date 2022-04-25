from aiogram.types import Message
from aiogram_dialog import DialogManager

from app import dp
from app.states.solution import SolutionDialog


@dp.message(commands="solution", is_registered=True)
async def solution_handler(message: Message, dialog_manager=DialogManager):
    await dialog_manager.start(SolutionDialog.link_request)
