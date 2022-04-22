from aiogram import types
from aiogram.dispatcher.filters import BaseFilter
from sqlalchemy import select

from app import owner_id, sessionmanager
from app.utils.db.models import User


class IsOwner(BaseFilter):
    is_owner: bool

    async def __call__(self, message: types.Message) -> bool:
        return self.is_owner is (message.from_user.id == owner_id)


class IsRegistered(BaseFilter):
    is_registered: bool

    async def __call__(self, message: types.Message) -> bool:
        async with sessionmanager() as session:
            registered = await session.scalar(
                select(User.registered).where(User.id == message.from_user.id)
            )
            return bool(registered) == self.is_registered
