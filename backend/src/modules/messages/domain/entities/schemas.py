from datetime import datetime
from typing import Annotated, Self
from uuid import UUID

from pydantic import Discriminator, Field, Tag, model_validator

from src.modules.messages.transport.http.utils import get_discriminator_value
from src.modules.messages.transport.http.validators import validate_target
from src.shared.domain.entity import Entity
from src.shared.schemas import BaseSchema


class MessageBase(BaseSchema):
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


class Message(Entity):
    def __init__(
        self,
        id: UUID,
        sender_id: UUID,
        body: str | None,
        sequence: int,
        parent_id: UUID | None,
        is_edited: bool,
        is_deleted: bool,
        deleted_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
        chat_id: UUID | None,
        channel_id: UUID | None,
    ) -> None:
        super().__init__(id)
        self.sender_id = sender_id
        self.body = body
        self.sequence = sequence
        self.parent_id = parent_id
        self.is_edited = is_edited
        self.is_deleted = is_deleted
        self.deleted_at = deleted_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.chat_id = chat_id
        self.channel_id = channel_id


class MessageCreateRequest(BaseSchema):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: UUID | None = None


class MessageCreate(BaseSchema):
    sender_id: UUID
    body: str
    sequence: int
    channel_id: UUID | None = None
    chat_id: UUID | None = None
    parent_id: UUID | None

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        validate_target(self)
        return self


class ChannelMessage(MessageBase):
    channel_id: UUID


class ChatMessage(MessageBase):
    chat_id: UUID


MessageResponse = Annotated[
    Annotated[ChannelMessage, Tag("channel")] | Annotated[ChatMessage, Tag("chat")],
    Discriminator(get_discriminator_value),
]
