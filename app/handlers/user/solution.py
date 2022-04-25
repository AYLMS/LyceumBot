from aiogram.types import Message
from aiogram_dialog import DialogManager

from app import dp, owner_id
from app.common import FMT
from app.keyboards.inline.invite_keyboard import get_invite_keyboard
from app.states.courses import CoursesDialog
from app.states.solution import SolutionDialog
from app.ui.commands import owner_commands, users_commands
from app.utils.api import get_user_information


@dp.message(commands="solution", is_registered=True)
async def solution_handler(message: Message, dialog_manager=DialogManager):
    await dialog_manager.start(SolutionDialog.link_request)