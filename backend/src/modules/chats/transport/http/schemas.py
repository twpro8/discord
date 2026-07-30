from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from src.modules.chats.domain.enums import ChatType
from src.shared.schemas import BaseSchema


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


class LastMessagePreviewResponse(BaseSchema):
    sender_id: UUID
    body: str | None
    created_at: datetime


class GroupChatSummaryResponse(BaseSchema):
    id: UUID
    type: Literal[ChatType.group]
    name: str
    image_url: str | None
    unread_count: int
    last_message: LastMessagePreviewResponse | None


class PrivateChatSummaryResponse(BaseSchema):
    id: UUID
    type: Literal[ChatType.private]
    peer_id: UUID
    peer_name: str
    peer_avatar_url: str | None
    unread_count: int
    last_message: LastMessagePreviewResponse | None


ChatSummaryResponse = Annotated[
    GroupChatSummaryResponse | PrivateChatSummaryResponse,
    Field(discriminator="type"),
]


class ChatSummaryPageResponse(BaseSchema):
    items: list[ChatSummaryResponse]
    next_cursor: str | None
    total: int
