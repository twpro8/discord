from typing import Any

from sqlalchemy import Row

from src.chat.enums import ChatType
from src.chat.models import ChatMemberOrm, ChatOrm
from src.chat.schemas import (
    Chat,
    ChatMember,
    ChatSummary,
    GroupChatSummary,
    LastMessagePreview,
    PrivateChatSummary,
)
from src.core.repositories.base_data_mapper import BaseMapper


class ChatMapper(BaseMapper[ChatOrm, Chat]):
    orm_class = ChatOrm
    schema_class = Chat


class MemberMapper(BaseMapper[ChatMemberOrm, ChatMember]):
    orm_class = ChatMemberOrm
    schema_class = ChatMember


class ChatSummaryMapper:
    @staticmethod
    def to_schema(row: Row[Any]) -> ChatSummary:
        last_message = (
            LastMessagePreview(
                sender_id=row.lm_sender_id,
                body=row.lm_body_snippet,
                created_at=row.lm_created_at,
            )
            if row.lm_created_at is not None
            else None
        )

        if row.type == ChatType.private:
            return PrivateChatSummary(
                id=row.id,
                type=row.type,
                peer_id=row.peer_id,
                peer_name=row.peer_name,
                peer_avatar_url=row.peer_avatar_url,
                unread_count=row.unread_count,
                last_message=last_message,
            )

        return GroupChatSummary(
            id=row.id,
            type=row.type,
            name=row.name,
            image_url=row.image_url,
            unread_count=row.unread_count,
            last_message=last_message,
        )
