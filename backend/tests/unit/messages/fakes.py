from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.core.realtime.envelope import EventType
from src.modules.messages.domain.entities.dtos import (
    ChannelMessagePage,
    ChatMessagePage,
    MessageCreate,
    channel_message_from_message,
    chat_message_from_message,
)
from src.modules.messages.domain.entities.message import Message


class FakeMessageRepository:
    def __init__(self) -> None:
        self.messages: dict[UUID, Message] = {}

    async def create(self, data: MessageCreate) -> Message:
        now = datetime.now(UTC)
        message = Message(
            id=uuid4(),
            sender_id=data.sender_id,
            body=data.body,
            sequence=data.sequence,
            parent_id=data.parent_id,
            is_edited=False,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
            chat_id=data.chat_id,
            channel_id=data.channel_id,
        )
        self.messages[message.id] = message
        return message

    async def get_by_id(self, message_id: UUID) -> Message | None:
        return self.messages.get(message_id)

    async def list_for_chat(
        self,
        chat_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChatMessagePage:
        items = self._page(chat_id, "chat_id", limit, before_cursor, after_cursor)
        return ChatMessagePage(
            items=[chat_message_from_message(m) for m in items],
            next_cursor=None,
            has_more=False,
        )

    async def list_for_channel(
        self,
        channel_id: UUID,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> ChannelMessagePage:
        items = self._page(channel_id, "channel_id", limit, before_cursor, after_cursor)
        return ChannelMessagePage(
            items=[channel_message_from_message(m) for m in items],
            next_cursor=None,
            has_more=False,
        )

    def _page(
        self,
        container_id: UUID,
        attr: str,
        limit: int,
        before_cursor: int | None,
        after_cursor: int | None,
    ) -> list[Message]:
        matches = [
            m for m in self.messages.values() if getattr(m, attr) == container_id
        ]
        matches.sort(key=lambda m: m.sequence)
        if before_cursor is not None:
            matches = [m for m in matches if m.sequence < before_cursor]
        if after_cursor is not None:
            matches = [m for m in matches if m.sequence > after_cursor]
        return matches[:limit]

    async def update_body(self, message_id: UUID, body: str) -> Message:
        message = self.messages[message_id]
        message.body = body
        message.is_edited = True
        message.updated_at = datetime.now(UTC)
        return message

    async def soft_delete(self, message_id: UUID) -> Message:
        message = self.messages[message_id]
        message.body = None
        message.is_deleted = True
        message.deleted_at = datetime.now(UTC)
        return message


class FakeRealtimeNotifier:
    def __init__(self) -> None:
        self.room_published: list[tuple[str, EventType, dict[str, Any]]] = []

    async def publish_to_room(
        self, room: str, event_type: EventType, payload: Mapping[str, Any]
    ) -> None:
        self.room_published.append((room, event_type, dict(payload)))
