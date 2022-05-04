from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Select,
    Back,
    Column,
    Url,
    ScrollingGroup,
    ListGroup,
    Cancel, Group,
)
from aiogram_dialog.widgets.text import Const, Format

from app import sessionmanager
from app.states.courses import CoursesDialog
from app.utils.api import (
    get_user_information,
    get_lessons_information,
    get_lesson_info,
    get_lesson_tasks, get_task_info,
)
from app.utils.staff import task_solution_type, sections_types, lesson_types, \
    solution_check_type


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

    dialog_manager.current_context().dialog_data[
        "user_information"] = user_information

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
            group_id = course["group"]["id"]

            dialog_manager.current_context().dialog_data["group_id"] = group_id

            lessons_json = await get_lessons_information(
                course_id, group_id, user.cookies
            )

            lessons = [(lesson["title"], lesson["id"]) for lesson in
                       lessons_json]

            teachers = ", ".join(
                [
                    f"{teacher['lastName']} {teacher['firstName']} {teacher['middleName']}"
                    for teacher in course["teachersList"]
                ]
            )
            return {
                "lessons": lessons,
                "title": course["title"],
                "course_id": course["id"],
                "group_id": group_id,
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


async def get_lesson_data(dialog_manager: DialogManager, **kwargs):
    async with sessionmanager() as session:
        user = await session.get_user(dialog_manager.event.from_user.id)

    lesson_id = dialog_manager.current_context().dialog_data["lesson_id"]
    group_id = dialog_manager.current_context().dialog_data["group_id"]
    course_id = dialog_manager.current_context().dialog_data["course_id"]

    lesson_data = await get_lesson_info(lesson_id, course_id, group_id,
                                        user.cookies)

    lesson_tasks = await get_lesson_tasks(lesson_id, course_id, group_id,
                                          user.cookies)

    tasks = []

    for section in lesson_tasks:
        tasks.append((sections_types[section["id"]], section["id"]))
        now = [
            (task_solution_type[str(task['solution']['status']['id']) if task[
                'solution'] else "6"] + ' ' + task[
                 'title'], task['id']) for task in section['tasks']]
        tasks.extend(now)

    return {
        "title": lesson_data["title"],
        "type": lesson_types[lesson_data["type"]],
        "score": lesson_data["score"],
        "num_tasks": lesson_data["numTasks"],
        "num_passed": lesson_data["numPassed"],
        "tasks": tasks,
    }


async def get_task_data(dialog_manager: DialogManager, **kwargs):
    async with sessionmanager() as session:
        user = await session.get_user(dialog_manager.event.from_user.id)

    task_id = dialog_manager.current_context().dialog_data["task_id"]
    group_id = dialog_manager.current_context().dialog_data["group_id"]

    task_data = await get_task_info(task_id, group_id, user.cookies)

    return {
        "title": task_data["title"],
        "lesson_title": task_data['lesson']['title'],
        "score_max": task_data['scoreMax'],
        "deadline": task_data['deadline'],
        "manual_check": solution_check_type[bool(task_data['hasManualCheck'])],
        "solution_id": task_data['solutionId'] if task_data['solutionId'] else None,
    }


async def lessons_selected(
        c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    manager.current_context().dialog_data["lesson_id"] = int(item_id)
    await manager.dialog().next()


async def task_selected(
        c: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    manager.current_context().dialog_data["task_id"] = int(item_id)
    await manager.dialog().next()


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
        Button(Const("🚫 Закрыть"), on_click=lambda c, b, m: m.done(),
               id="close"),
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
        Format(
            "<b>Количество отправленных на доработку</b>: <code>{numRework}</code>"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="lesson_select",
                item_id_getter=lambda x: x[1],
                items="lessons",
                on_click=lessons_selected,
            ),
            width=1,
            height=10,
            id="lesson_select_group",
        ),
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
        Cancel(Const("🚫 Закрыть")),
        getter=get_course_data,
        state=CoursesDialog.course_info,
    ),
    Window(
        Const("<b>Информация по уроку</b>"),
        Format("<b>Название</b>: <code>{title}</code>"),
        Format("<b>Тип</b>: <code>{type}</code>"),
        Format("<b>Балл</b>: <code>{score}</code>"),
        Format("<b>Всего задач</b>: <code>{num_tasks}</code>"),
        Format("<b>Решено задач</b>: <code>{num_passed}</code>"),
        Group(
            Select(
                Format("{item[0]}"),
                id="tasks_select",
                item_id_getter=lambda x: x[1],
                items="tasks",
                on_click=task_selected,
            ),
            width=1,
        ),
        Back(Const("🔙 Назад")),
        Cancel(Const("🚫 Закрыть")),
        getter=get_lesson_data,
        state=CoursesDialog.lesson_info,
    ),
    Window(
        Const("<b>Информация по задаче</b> \n"),
        Format("<b>Название урока</b>: <code>{lesson_title}</code>"),
        Format("<b>Название задачи</b>: <code>{title}</code>\n"),
        Format("<b>Максимальный балл</b>: <code>{score_max}</code>"),
        Format("<b>Дедлайн</b>: <code>{deadline}</code>"),
        Format("<b>Тип проверки</b>: <code>{manual_check}</code>"),
        Format("<b>ID решения</b>: <code>{solution_id}</code>"),
        Back(Const("🔙 Назад")),
        Cancel(Const("🚫 Закрыть")),
        getter=get_task_data,
        state=CoursesDialog.task_info,
    )
)
