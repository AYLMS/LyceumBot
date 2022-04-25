from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Select, Back, Column, Url
from aiogram_dialog.widgets.text import Const, Format

from app import sessionmanager
from app.states.courses import CoursesDialog
from app.utils.api import get_user_information


async def on_course_selected(
    c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    manager.current_context().dialog_data["course_id"] = int(item_id)
    await manager.dialog().next()


async def get_data(dialog_manager: DialogManager, **kwargs):
    async with sessionmanager() as session:
        user = await session.get_user(dialog_manager.event.from_user.id)

    user_information: dict = (
        dialog_manager.current_context().dialog_data["user_information"]
        if "user_information" in dialog_manager.current_context().dialog_data
        else await get_user_information(
            with_courses_summary=True,
            with_expelled=True,
            with_children=False,
            with_parents=False,
            cookies=user.cookies,
        )
    )

    dialog_manager.current_context().dialog_data["user_information"] = user_information

    courses = [
        (course["title"], course["id"])
        for course in user_information["coursesSummary"]["student"]
    ]

    return {
        "courses": courses,
    }


async def get_course_data(dialog_manager: DialogManager, **kwargs):
    async with sessionmanager() as session:
        user = await session.get_user(dialog_manager.event.from_user.id)
    user_information: dict = dialog_manager.current_context().dialog_data[
        "user_information"
    ]

    course_id = dialog_manager.current_context().dialog_data["course_id"]

    for course in user_information["coursesSummary"]["student"]:
        if course["id"] == course_id:
            teachers = ", ".join(
                [
                    f"{teacher['lastName']} {teacher['firstName']} {teacher['middleName']}"
                    for teacher in course["teachersList"]
                ]
            )
            return {
                "title": course["title"],
                "course_id": course["id"],
                "group_id": course["group"]["id"],
                "group_name": course["group"]["name"],
                "rating": round(float(course["rating"]), 2),
                "bonusScore": course["bonusScore"],
                "numTasks": course["progress"]["numTasks"],
                "numPassed": course["progress"]["numPassed"],
                "numRework": course["progress"]["numRework"],
                "teachers": teachers,
                "cert_number": course["certificateNumber"],
                "last_name": user_information["profile"]["lastName"],
            }


courses_select = Column(
    Select(
        Format("{item[0]}"),
        id="courses_select",
        item_id_getter=lambda x: x[1],
        items="courses",
        on_click=on_course_selected,
    )
)

ui = Dialog(
    Window(
        Const("<b>📌 Выберите курс</b>"),
        courses_select,
        Button(Const("🚫 Закрыть"), on_click=lambda c, b, m: m.done(), id="close"),
        getter=get_data,
        state=CoursesDialog.select_courses,
    ),
    Window(
        Format("<b>ℹ️ {title}</b> \n"),
        Format("<b>👥 Группа</b>:  <code>{group_name}</code>"),
        Format("<b>👥 Учителя</b>:  <code>{teachers}</code>", when="teachers"),
        Format("<b>🎯 Рейтинг</b>:  <code>{rating}</code> \n"),
        Format("<b>Бонусные баллы</b>: <code>{bonusScore}</code>"),
        Format("<b>Количество отправок</b>: <code>{numTasks}</code>"),
        Format("<b>Количество принятых отправок</b>: <code>{numPassed}</code>"),
        Format("<b>Количество отправленных на доработку</b>: <code>{numRework}</code>"),
        Url(
            Const("🔗 Открыть"),
            url=Format(
                "https://lyceum.yandex.ru/courses/{course_id}/groups/{group_id}"
            ),
        ),
        Url(
            Const("📄 Сертификат"),
            url=Format(
                "https://lyceum.yandex.ru/certificate/check/?certNumber={cert_number}&lastName={last_name}",
            ),
            when="cert_number",
        ),
        Back(Const("🔙 Назад")),
        Button(Const("🚫 Закрыть"), on_click=lambda c, b, m: m.done(), id="close"),
        getter=get_course_data,
        state=CoursesDialog.course_info,
    ),
)
