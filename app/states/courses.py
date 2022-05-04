from aiogram.dispatcher.fsm.state import State, StatesGroup


class CoursesDialog(StatesGroup):
    select_courses = State()
    course_info = State()
    lesson_info = State()
    task_info = State()
