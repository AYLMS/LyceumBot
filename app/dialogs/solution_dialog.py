from aiogram.types import Message, URLInputFile
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog import Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from app import sessionmanager, bot
from app.states.solution import SolutionDialog
from app.utils.api import get_solution_information
from app.utils.staff import solution_type, solution_verdict


async def solution_id_handler(
    m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    if "http" in m.text:
        manager.current_context().dialog_data["solution_id"] = m.text.split("/")[-1]
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
    file_url = solution_data["solution"]["latestSubmission"]["file"]["url"]
    await bot.send_document(user_id, URLInputFile(file_url, file_url.split("/")[-1]))
    print(solution_data)
    return {
        "test_result": solution_data["solution"]["status"]["type"],
        "problem_name": solution_data["solution"]["task"]["title"],
        "problem_tag": solution_type[solution_data["solution"]["task"]["tag"]["type"]],
        "score_max": solution_data["solution"]["task"]["scoreMax"],
        "deadline": solution_data["solution"]["task"]["lesson"]["deadline"],
        "send_time": solution_data["solution"]["latestSubmission"]["file"]["addedTime"],
        "verdict": solution_verdict[solution_data["solution"]["latestSubmission"]["verdict"]],
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
        Format("<b>🗂 Тип задачи</b>:  <code>{problem_tag}</code> \n"),
        Format("<b>🎯 Максимальный балл за задачу </b>:  <code>{score_max}</code>"),
        Format("<b>Вердикт</b>: <code>{verdict}</code>"),
        Format("<b>✉️ Дата отправки</b>: <code>{send_time}</code>"),
        Format("<b>📅 Дедлайн</b>: <code>{deadline}</code>"),
        Button(Const("🚫 Закрыть"), on_click=lambda c, b, m: m.done(), id="close"),
        state=SolutionDialog.solution_info,
        getter=get_solution_data,
    ),
)
