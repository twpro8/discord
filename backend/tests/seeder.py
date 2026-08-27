from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base
from src.modules.users.adapters.persistence.models import UserOrm
from src.shared.schemas import BaseSchema
from tests.data import users


class _UserSeedRow(BaseSchema):
    """Coerces raw JSON seed data (string UUIDs/timestamps) into the typed
    values SQLAlchemy's Core insert() needs. Deliberately independent of the
    User domain entity, which is a plain object with no such coercion."""

    id: UUID
    name: str
    username: str
    email: str
    password_hash: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


async def populate_database(session: AsyncSession) -> None:
    await seed(session, UserOrm, _UserSeedRow, users)
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
