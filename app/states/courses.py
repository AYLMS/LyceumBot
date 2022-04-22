from aiogram.dispatcher.fsm.state import State, StatesGroup


class CoursesDialog(StatesGroup):
    select_courses = State()
    course_info = State()
