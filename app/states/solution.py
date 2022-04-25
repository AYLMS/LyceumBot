from aiogram.dispatcher.fsm.state import State, StatesGroup


class SolutionDialog(StatesGroup):
    link_request = State()
    solution_info = State()
