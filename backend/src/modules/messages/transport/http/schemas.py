from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Discriminator, Field, Tag

from src.modules.messages.transport.http.utils import get_discriminator_value
from src.shared.schemas import BaseSchema


class MessageCreateRequest(BaseSchema):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: UUID | None = None


class MessageEditRequest(BaseSchema):
    body: str = Field(min_length=1, max_length=2000)


class MessageBaseResponse(BaseSchema):
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


class ChannelMessageResponse(MessageBaseResponse):
    channel_id: UUID


class ChatMessageResponse(MessageBaseResponse):
    chat_id: UUID


MessageResponse = Annotated[
    Annotated[ChannelMessageResponse, Tag("channel")]
    | Annotated[ChatMessageResponse, Tag("chat")],
    Discriminator(get_discriminator_value),
]


class ChatMessagePageResponse(BaseSchema):
    items: list[ChatMessageResponse]
    next_cursor: str | None
    has_more: bool


class ChannelMessagePageResponse(BaseSchema):
    items: list[ChannelMessageResponse]
    next_cursor: str | None
    has_more: bool
