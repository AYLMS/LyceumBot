from aiogram.types import Message
from aiogram_dialog import DialogManager

from app import dp, owner_id
from app.common import FMT
from app.keyboards.inline.invite_keyboard import get_invite_keyboard
from app.states.courses import CoursesDialog
from app.ui.commands import owner_commands, users_commands
from app.utils.api import get_user_information


@dp.message(commands="help")
async def help_handler(message: Message):
    text = "ℹ️ <b>Список команд:</b> \n\n"
    commands = (
        owner_commands.items()
        if message.from_user.id == owner_id
        else users_commands.items()
    )
    for command, description in commands:
        text += f"/{command} - <b>{description}</b> \n"
    await message.answer(text)


@dp.message(commands="info", is_registered=True)
async def info_handler(message: Message, f: FMT):
    user = await f.db.get_user(message.from_user.id)
    user_information = await get_user_information(
        with_courses_summary=False,
        with_expelled=False,
        with_children=False,
        with_parents=False,
        cookies=user.cookies
    )
    await message.answer(
        "<b>ℹ️ Информация о пользователе:</b> \n\n"
        f"<b>ФИО:</b> {user_information['profile']['lastName']} {user_information['profile']['firstName']} {user_information['profile']['middleName']} \n"
        f" <b>E-mail:</b> {user_information['profile']['email']} \n"
        f" <b>Телефон:</b> {user_information['profile']['phone']} \n"
    )


@dp.message(commands="parents", is_registered=True)
async def parents_handler(message: Message, f: FMT):
    user = await f.db.get_user(message.from_user.id)
    user_information = await get_user_information(
        with_courses_summary=False,
        with_expelled=False,
        with_children=False,
        with_parents=True,
        cookies=user.cookies
    )
    text = ''
    if user_information['profile']['parents']:
        text += "ℹ️ <b>Информация о родителях:</b> \n\n"
        for parent in user_information['profile']['parents']:
            text += f"▫️ <b>ФИО:</b> {parent['lastName']} {parent['firstName']} {parent['middleName']} \n"
            text += f"       <b>Телефон:</b> {parent['phone']} \n" if parent['phone'] else ""
            text += f"       <b>E-mail:</b> {parent['email']} \n" if parent['email'] else ""
            text += "\n"

    text += f"🎚 <b>Родителей добавлено: {user_information['profile']['invite']['usesCount']}/{user_information['profile']['invite']['usesLimit']}</b>\n\n"
    await message.answer(text, reply_markup=get_invite_keyboard(user_information['profile']['invite']['url']))


@dp.message(commands="courses", is_registered=True)
async def register_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(CoursesDialog.select_courses)

