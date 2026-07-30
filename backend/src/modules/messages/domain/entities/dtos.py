from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.modules.messages.domain.entities.message import Message


@dataclass(frozen=True, kw_only=True)
class MessageCreateData:
    """Mirrors the transport-layer create request; used as a Command field."""

    body: str
    parent_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class MessageCreate:
    """Persistence payload for a new message. Exactly one of chat_id/channel_id
    must be set — this was previously enforced by a Pydantic validator."""

    sender_id: UUID
    body: str
    sequence: int
    parent_id: UUID | None
    channel_id: UUID | None = None
    chat_id: UUID | None = None

    def __post_init__(self) -> None:
        if (self.chat_id is None) == (self.channel_id is None):
            raise ValueError(
                "Exactly one of 'chat_id' or 'channel_id' must be provided."
            )


@dataclass(frozen=True, kw_only=True)
class MessageBase:
    id: UUID
    sender_id: UUID
    body: str | None
    sequence: int
    parent_id: UUID | None
    is_edited: bool
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, kw_only=True)
class ChannelMessage(MessageBase):
    channel_id: UUID


@dataclass(frozen=True, kw_only=True)
class ChatMessage(MessageBase):
    chat_id: UUID


def channel_message_from_message(message: Message) -> ChannelMessage:
    assert message.channel_id is not None
    return ChannelMessage(
        id=message.id,
        sender_id=message.sender_id,
        body=message.body,
        sequence=message.sequence,
        parent_id=message.parent_id,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        deleted_at=message.deleted_at,
        created_at=message.created_at,
        updated_at=message.updated_at,
        channel_id=message.channel_id,
    )


def chat_message_from_message(message: Message) -> ChatMessage:
    assert message.chat_id is not None
    return ChatMessage(
        id=message.id,
        sender_id=message.sender_id,
        body=message.body,
        sequence=message.sequence,
        parent_id=message.parent_id,
        is_edited=message.is_edited,
        is_deleted=message.is_deleted,
        deleted_at=message.deleted_at,
        created_at=message.created_at,
        updated_at=message.updated_at,
        chat_id=message.chat_id,
    )
