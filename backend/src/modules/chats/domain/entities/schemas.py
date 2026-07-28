from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.shared.schemas.base_schema import BaseSchema


class MemberCreate(BaseSchema):
    user_id: UUID
    chat_id: UUID
    role: ChatMemberRole | None = ChatMemberRole.member


class ChatCreate(BaseSchema):
    owner_id: UUID | None = None
    type: ChatType
    name: str | None = None
    description: str | None = None


class ChatCreateRequest(BaseSchema):
    type: ChatType
    target_user_id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=300)
    member_ids: list[UUID] | None = None

    @model_validator(mode="after")
    def validate_conditional_fields(self) -> ChatCreateRequest:
        if self.type == ChatType.private:
            if self.target_user_id is None:
                raise ValueError("'target_user_id' is required when type is 'private'.")
            if self.name is not None:
                raise ValueError("'name' is only allowed for group chats.")
            if self.description is not None:
                raise ValueError("'description' is only allowed for group chats.")
            if self.member_ids is not None:
                raise ValueError("'member_ids' is only allowed for group chats.")

        elif self.type == ChatType.group:
            if self.name is None:
                raise ValueError("'name' is required when type is 'group'.")
            if self.target_user_id is not None:
                raise ValueError("'target_user_id' is only allowed for private chats.")

        return self


class LastMessagePreview(BaseSchema):
    sender_id: UUID
    body: str | None
    created_at: datetime


class GroupChatSummary(BaseSchema):
    id: UUID
    type: Literal[ChatType.group]
    name: str
    image_url: str | None
    unread_count: int
    last_message: LastMessagePreview | None


class PrivateChatSummary(BaseSchema):
    id: UUID
    type: Literal[ChatType.private]
    peer_id: UUID
    peer_name: str
    peer_avatar_url: str | None
    unread_count: int
    last_message: LastMessagePreview | None


ChatSummary = Annotated[
    GroupChatSummary | PrivateChatSummary,
    Field(discriminator="type"),
]


class ChatSummaryPage(BaseSchema):
    items: list[ChatSummary]
    next_cursor: str | None
    total: int
