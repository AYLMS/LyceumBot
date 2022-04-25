from typing import Any

from aiogram.types import CallbackQuery, Message, ContentType, URLInputFile
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog import Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Back, Column, Url
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from aiohttp import ClientSession

from app import sessionmanager, bot
from app.states.solution import SolutionDialog
from app.utils.api import get_user_information, get_solution_information


async def solution_id_handler(
        m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    if 'http' in m.text:
        manager.current_context().dialog_data["solution_id"] = \
            m.text.split('/')[-1]
    else:
        manager.current_context().dialog_data["solution_id"] = m.text
    await dialog.next()


async def get_solution_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    solution_id = dialog_manager.current_context().dialog_data["solution_id"]
    async with sessionmanager() as session:
        user = await session.get_user(user_id)

    cookies = user.cookies
    solution_data = await get_solution_information(solution_id, cookies)
    file_url = solution_data['solution']['latestSubmission']['file']['url']
    await bot.send_document(
        user_id,
        URLInputFile(
            file_url,
            file_url.split('/')[-1]
        )
    )
    return {
        'test_result': solution_data['solution']['status']['type'],
        'problem_name': solution_data['solution']['task']['title'],
        'problem_tags': type[solution_data['solution']['task']['tag']['type']],
        'score_max': solution_data['solution']['task']['scoreMax'],
        'deadline': solution_data['solution']['task']['lesson']['deadline'],
    }


ui = Dialog(
    Window(
        Const("<b> 👨🏻‍💻 Введите id решения или ссылку</b>"),
        MessageInput(solution_id_handler),
        state=SolutionDialog.link_request,
    ),
    Window(
        Format("<b>ℹ️ Информация о решении</b> \n"),
        Format("<b>✏️ Название задачи</b>:  <code>{problem_name}</code>"),
        Format("<b> Тип задачи</b>:  <code>{problem_tags}</code>", when="teachers"),
        Format("<b>🎯 Максимальный балл за задачу </b>:  <code>{score_max}</code> \n"),
        # Format("<b>Бонусные баллы</b>: <code>{bonusScore}</code>"),
        Format("<b>📅 Дедлайн</b>: <code>{deadline}</code>"),
        Button(Const("🚫 Закрыть"), on_click=lambda c, b, m: m.done(),
               id="close"),
        state=SolutionDialog.solution_info,
        getter=get_solution_data,
    )
)
