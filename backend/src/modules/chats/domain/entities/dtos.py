from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.shared.domain.unset import UNSET, Unsettable


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


@dataclass(frozen=True, kw_only=True)
class ChatUpdateData:
    name: Unsettable[str] = UNSET
    description: Unsettable[str] = UNSET
    image_url: Unsettable[str] = UNSET


@dataclass(frozen=True, kw_only=True)
class ChatUpdate(ChatUpdateData):
    owner_id: Unsettable[UUID] = UNSET
    is_archived: Unsettable[bool] = UNSET


@dataclass(frozen=True, kw_only=True)
class ChatMemberSummary:
    user_id: UUID
    username: str
    display_name: str
    avatar_url: str | None
    role: ChatMemberRole
    joined_at: datetime


@dataclass(frozen=True, kw_only=True)
class AddMemberResult:
    added: list[UUID]
    skipped: list[UUID]
