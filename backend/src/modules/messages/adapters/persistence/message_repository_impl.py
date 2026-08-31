from dataclasses import asdict
from datetime import UTC, datetime
from uuid import UUID

from asyncpg.exceptions import ForeignKeyViolationError
from sqlalchemy import ColumnElement, Executable, insert, select, update
from sqlalchemy.exc import IntegrityError

from src.modules.messages.adapters.persistence.mappers import MessageDataMapper
from src.modules.messages.adapters.persistence.models import MessageOrm
from src.modules.messages.domain.cursor import encode_cursor
from src.modules.messages.domain.entities.dtos import (
    ChannelMessage,
    ChannelMessagePage,
    ChatMessage,
    ChatMessagePage,
    MessageCreate,
    channel_message_from_message,
    chat_message_from_message,
)
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.domain.exceptions import MessageNotFoundError
from src.shared.adapters.base_repository import BaseRepository


class MessageRepositoryImpl(BaseRepository[MessageOrm, Message, MessageCreate, None]):
    _model = MessageOrm
    _mapper = MessageDataMapper

    async def create(self, data: MessageCreate) -> Message:
        stmt = insert(MessageOrm).values(**asdict(data)).returning(MessageOrm)
        try:
            result = await self._session.execute(stmt)
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, ForeignKeyViolationError):
                match constraint:
                    case "messages_parent_id_fkey":
                        raise MessageNotFoundError
                raise
            raise
        return MessageDataMapper.to_entity(result.scalar_one())

    async def _fetch_page(
        self,
        container_filter: ColumnElement[bool],
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> tuple[list[Message], str | None, bool]:
        query: Executable
        if before_cursor is not None:
            query = (
                select(MessageOrm)
                .where(container_filter, MessageOrm.sequence < before_cursor)
                .order_by(MessageOrm.sequence.desc())
                .limit(limit + 1)
            )
        else:
            floor = after_cursor if after_cursor is not None else 0
            query = (
                select(MessageOrm)
                .where(container_filter, MessageOrm.sequence > floor)
                .order_by(MessageOrm.sequence.asc())
                .limit(limit + 1)
            )

        rows = (await self._session.execute(query)).scalars().all()
        has_more = len(rows) > limit
        rows = rows[:limit]

        if before_cursor is not None:
            items = [MessageDataMapper.to_entity(m) for m in reversed(rows)]
            next_cursor = (
                encode_cursor(items[0].sequence) if has_more and items else None
            )
        else:
            items = [MessageDataMapper.to_entity(m) for m in rows]
            next_cursor = (
                encode_cursor(items[-1].sequence) if has_more and items else None
            )

        return items, next_cursor, has_more

    async def list_for_chat(
        self,
        chat_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChatMessagePage:
        items, next_cursor, has_more = await self._fetch_page(
            MessageOrm.chat_id == chat_id, limit, before_cursor, after_cursor
        )
        chat_items: list[ChatMessage] = [chat_message_from_message(m) for m in items]
        return ChatMessagePage(
            items=chat_items, next_cursor=next_cursor, has_more=has_more
        )

    async def list_for_channel(
        self,
        channel_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChannelMessagePage:
        items, next_cursor, has_more = await self._fetch_page(
            MessageOrm.channel_id == channel_id, limit, before_cursor, after_cursor
        )
        channel_items: list[ChannelMessage] = [
            channel_message_from_message(m) for m in items
        ]
        return ChannelMessagePage(
            items=channel_items, next_cursor=next_cursor, has_more=has_more
        )

    async def update_body(self, message_id: UUID, body: str) -> Message:
        stmt = (
            update(MessageOrm)
            .where(MessageOrm.id == message_id)
            .values(body=body, is_edited=True, updated_at=datetime.now(UTC))
            .returning(MessageOrm)
        )
        result = await self._session.execute(stmt)
        return MessageDataMapper.to_entity(result.scalar_one())

    async def soft_delete(self, message_id: UUID) -> Message:
        stmt = (
            update(MessageOrm)
            .where(MessageOrm.id == message_id)
            .values(body=None, is_deleted=True, deleted_at=datetime.now(UTC))
            .returning(MessageOrm)
        )
        result = await self._session.execute(stmt)
        return MessageDataMapper.to_entity(result.scalar_one())
