from typing import Any

from sqlalchemy import Row

from src.core.repositories.base_data_mapper import BaseMapper
from src.chat.schemas import (
    Chat,
    ChatMember,
    ChatSummary,
    LastMessagePreview,
)
from src.chat.models import ChatOrm, ChatMemberOrm


class ChatMapper(BaseMapper[ChatOrm, Chat]):
    orm_class = ChatOrm
    schema_class = Chat


class MemberMapper(BaseMapper[ChatMemberOrm, ChatMember]):
    orm_class = ChatMemberOrm
    schema_class = ChatMember


class ChatSummaryMapper:
    @staticmethod
    def to_schema(row: Row[Any]) -> ChatSummary:
        return ChatSummary(
            id=row.id,
            type=row.type,
            name=row.name,
            image_url=row.image_url,
            unread_count=row.unread_count,
            last_message=(
                LastMessagePreview(
                    sender_id=row.lm_sender_id,
                    body=row.lm_body_snippet,
                    created_at=row.lm_created_at,
                )
                if row.lm_created_at is not None
                else None
            ),
        )
