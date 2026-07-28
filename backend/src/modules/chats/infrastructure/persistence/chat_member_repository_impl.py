from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chats.domain.entities.chat import ChatMember
from src.modules.chats.domain.entities.schemas import MemberCreate
from src.modules.chats.infrastructure.persistence.mappers import (
    chat_member_model_to_entity,
)
from src.modules.chats.infrastructure.persistence.models import ChatMemberOrm


class ChatMemberRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_members(self, members: list[MemberCreate]) -> None:
        stmt = insert(ChatMemberOrm).values([m.model_dump() for m in members])
        await self._session.execute(stmt)

    async def find_active(self, chat_id: UUID, user_id: UUID) -> ChatMember | None:
        query = select(ChatMemberOrm).filter_by(
            user_id=user_id,
            chat_id=chat_id,
            left_at=None,
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return chat_member_model_to_entity(model) if model else None
