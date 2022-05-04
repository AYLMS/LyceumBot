import pickle

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog import Window
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Next, SwitchTo, Button
from aiogram_dialog.widgets.text import Const, Format
from requests import Session

from app import sessionmanager, bot
from app.states.register import RegistrationDialog


async def login_handler(
    m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    manager.current_context().dialog_data["login"] = m.text
    await dialog.next()


async def password_handler(
    m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager
):
    manager.current_context().dialog_data["password"] = m.text
    await dialog.next()


async def get_user_information(dialog_manager: DialogManager, **kwargs):
    return {
        "login": dialog_manager.current_context().dialog_data["login"],
        "password": dialog_manager.current_context().dialog_data["password"],
    }


async def login(c: CallbackQuery, button: Button, manager: DialogManager):
    login = manager.current_context().dialog_data["login"]
    password = manager.current_context().dialog_data["password"]
    request_session = Session()
    request = request_session.post(
        "https://passport.yandex.ru/auth", data={"login": login, "passwd": password}
    )
    if request.status_code == 200:
        pickle_dump = pickle.dumps(request_session.cookies)
        async with sessionmanager() as session:
            await session.change_user(c.from_user.id, "cookies", pickle_dump)
            await session.change_user(c.from_user.id, "registered", True)
        await manager.done()
        await bot.send_message(
            c.from_user.id,
            "<b>✅ Вы успешно зарегистрировались в системе.</b> \n\n"
            "Теперь вы можете использовать все возможности бота. \n\n"
            "<b>🎛 Полный список команд -</b> /help",
        )


ui = Dialog(
    Window(
        Const("<b>🔐 Авторизация через Yandex ID</b>"),
        Next(Const("🚀 Начать")),
        state=RegistrationDialog.greeting,
    ),
    Window(
        Const("<b> 👨🏻‍💻 Введите ваш логин</b>"),
        MessageInput(login_handler),
        state=RegistrationDialog.login_page,
    ),
    Window(
        Const("<b> 🔐 Введите ваш пароль</b>"),
        MessageInput(password_handler),
        state=RegistrationDialog.password_page,
    ),
    Window(
        Const("<b>ℹ️ Ваши данные: </b> \n"),
        Format("<b>👨🏻‍💻 Логин:</b> <code>{login}</code>"),
        Format("<b>🔐 Пароль: <code>{password}</code></b>"),
        SwitchTo(
            Const("✍️ Изменить"),
            state=RegistrationDialog.login_page,
            id="change_information",
        ),
        Button(Const("✅ Подтвердить"), on_click=login, id="confirm"),
        getter=get_user_information,
        state=RegistrationDialog.confirmation_page,
    ),
)
