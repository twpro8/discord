from dataclasses import asdict
from uuid import UUID

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.chats.adapters.persistence.mappers import ChatMemberDataMapper
from src.modules.chats.adapters.persistence.models import ChatMemberOrm
from src.modules.chats.domain.entities.chat import ChatMember
from src.modules.chats.domain.entities.dtos import ChatMemberSummary, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole
from src.modules.users.adapters.persistence.models import UserOrm


class ChatMemberRepositoryImpl:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_members(self, members: list[MemberCreate]) -> None:
        stmt = insert(ChatMemberOrm).values([asdict(m) for m in members])
        await self._session.execute(stmt)

    async def find_active(self, chat_id: UUID, user_id: UUID) -> ChatMember | None:
        query = select(ChatMemberOrm).filter_by(
            user_id=user_id,
            chat_id=chat_id,
            left_at=None,
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChatMemberDataMapper.to_entity(model) if model else None

    async def list_active_with_user(self, chat_id: UUID) -> list[ChatMemberSummary]:
        query = (
            select(
                ChatMemberOrm.user_id,
                UserOrm.username,
                UserOrm.name.label("display_name"),
                UserOrm.avatar_url,
                ChatMemberOrm.role,
                ChatMemberOrm.joined_at,
            )
            .join(UserOrm, UserOrm.id == ChatMemberOrm.user_id)
            .where(ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.left_at.is_(None))
            .order_by(ChatMemberOrm.joined_at)
        )
        rows = (await self._session.execute(query)).all()
        return [
            ChatMemberSummary(
                user_id=row.user_id,
                username=row.username,
                display_name=row.display_name,
                avatar_url=row.avatar_url,
                role=ChatMemberRole(row.role),
                joined_at=row.joined_at,
            )
            for row in rows
        ]

    async def list_active_user_ids(self, chat_id: UUID) -> set[UUID]:
        query = select(ChatMemberOrm.user_id).where(
            ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.left_at.is_(None)
        )
        result = await self._session.execute(query)
        return set(result.scalars().all())

    async def remove(self, chat_id: UUID, user_id: UUID) -> None:
        stmt = delete(ChatMemberOrm).where(
            ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.user_id == user_id
        )
        await self._session.execute(stmt)

    async def count_active(self, chat_id: UUID) -> int:
        query = select(func.count()).where(
            ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.left_at.is_(None)
        )
        result = await self._session.execute(query)
        return result.scalar_one()

    async def find_oldest_active_excluding(
        self, chat_id: UUID, exclude_user_id: UUID
    ) -> ChatMember | None:
        query = (
            select(ChatMemberOrm)
            .where(
                ChatMemberOrm.chat_id == chat_id,
                ChatMemberOrm.left_at.is_(None),
                ChatMemberOrm.user_id != exclude_user_id,
            )
            .order_by(ChatMemberOrm.joined_at)
            .limit(1)
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChatMemberDataMapper.to_entity(model) if model else None

    async def update_role(self, member_id: UUID, role: ChatMemberRole) -> None:
        stmt = (
            update(ChatMemberOrm).where(ChatMemberOrm.id == member_id).values(role=role)
        )
        await self._session.execute(stmt)

    async def update_last_read_seq(
        self, chat_id: UUID, user_id: UUID, up_to_seq: int
    ) -> None:
        stmt = (
            update(ChatMemberOrm)
            .where(ChatMemberOrm.chat_id == chat_id, ChatMemberOrm.user_id == user_id)
            .values(last_read_seq=func.greatest(ChatMemberOrm.last_read_seq, up_to_seq))
        )
        await self._session.execute(stmt)
