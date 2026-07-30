from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from src.modules.chats.domain.enums import ChatMemberRole, ChatType


@dataclass(frozen=True, kw_only=True)
class MemberCreate:
    user_id: UUID
    chat_id: UUID
    role: ChatMemberRole | None = ChatMemberRole.member


@dataclass(frozen=True, kw_only=True)
class ChatCreate:
    type: ChatType
    owner_id: UUID | None = None
    name: str | None = None
    description: str | None = None


@dataclass(frozen=True, kw_only=True)
class ChatCreateData:
    """Mirrors the transport-layer create request; used as a Command field."""

    type: ChatType
    target_user_id: UUID | None = None
    name: str | None = None
    description: str | None = None
    member_ids: list[UUID] | None = None


@dataclass(frozen=True, kw_only=True)
class LastMessagePreview:
    sender_id: UUID
    body: str | None
    created_at: datetime


@dataclass(frozen=True, kw_only=True)
class GroupChatSummary:
    id: UUID
    type: Literal[ChatType.group]
    name: str
    image_url: str | None
    unread_count: int
    last_message: LastMessagePreview | None


@dataclass(frozen=True, kw_only=True)
class PrivateChatSummary:
    id: UUID
    type: Literal[ChatType.private]
    peer_id: UUID
    peer_name: str
    peer_avatar_url: str | None
    unread_count: int
    last_message: LastMessagePreview | None


ChatSummary = GroupChatSummary | PrivateChatSummary


@dataclass(frozen=True, kw_only=True)
class ChatSummaryPage:
    items: list[ChatSummary]
    next_cursor: str | None
    total: int
