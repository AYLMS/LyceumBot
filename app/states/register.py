from aiogram.dispatcher.fsm.state import State, StatesGroup


class RegistrationDialog(StatesGroup):
    greeting = State()
    login_page = State()
    password_page = State()
    confirmation_page = State()
