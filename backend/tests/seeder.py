from typing import Any

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.kernel.postgres import Base
from src.kernel.schemas import BaseSchema
from src.modules.users.models import UserOrm
from src.modules.users.schemas import User
from tests.data import users


async def populate_database(session: AsyncSession) -> None:
    await seed(session, UserOrm, User, users)
    # await seed(session, GuildOrm, GuildSchema, guilds)
    # await seed(session, ChannelOrm, ChannelSchema, channels)

    await session.commit()


async def seed(
    session: AsyncSession,
    orm_model: type[Base],
    schema: type[BaseSchema],
    data: list[dict[str, Any]],
) -> None:
    await session.execute(
        insert(orm_model),
        [schema.model_validate(item).model_dump() for item in data],
    )
