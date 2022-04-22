import pickle

from aiogram.types import Message
from aiohttp import ClientSession as Session

from app import dp, owner_id
from app.common import FMT
from app.keyboards.inline.invite_keyboard import get_invite_keyboard
from app.ui.commands import owner_commands, users_commands


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


@dp.message(commands="info")
async def info_handler(message: Message, f: FMT):
    user = await f.db.get_user(message.from_user.id)
    cookies = pickle.loads(user.cookies)
    session = Session(cookies=cookies)
    user_information = await (
        await session.get(
            "https://lyceum.yandex.ru/api/profile",
            params={
                "withCoursesSummary": "false",
                "withExpelled": "false",
                "withChildren": "false",
                "withParents": "false",
            },
        )
    ).json()
    await message.answer(
        "<b>ℹ️ Информация о пользователе:</b> \n\n"
        f"<b>ФИО:</b> {user_information['profile']['lastName']} {user_information['profile']['firstName']} {user_information['profile']['middleName']} \n"
        f" <b>E-mail:</b> {user_information['profile']['email']} \n"
        f" <b>Телефон:</b> {user_information['profile']['phone']} \n"
    )



