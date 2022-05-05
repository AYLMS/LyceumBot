from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_course_keyboard(course_id, group_id, lesson_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔗 Открыть",
        url=f"https://lyceum.yandex.ru/courses/{course_id}/groups/{group_id}/lessons/{lesson_id}",
    )
    return keyboard.as_markup()


def get_task_keyboard(course_id, group_id, lesson_id, task_id, solution_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔗 Открыть",
        url=f"https://lyceum.yandex.ru/courses/{course_id}/groups/{group_id}/lessons/{lesson_id}/tasks/{task_id}/solutions/{solution_id}",
    )
    return keyboard.as_markup()
