from typing import Any, cast

from sqlalchemy import Row

from src.modules.chats.adapters.persistence.models import ChatMemberOrm, ChatOrm
from src.modules.chats.domain.entities.chat import Chat, ChatMember
from src.modules.chats.domain.entities.dtos import (
    ChatSummary,
    GroupChatSummary,
    LastMessagePreview,
    PrivateChatSummary,
)
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.shared.adapters.data_mapper import DataMapper


class ChatDataMapper(DataMapper[ChatOrm, Chat]):
    @staticmethod
    def to_entity(model: ChatOrm) -> Chat:
        return Chat(
            id=model.id,
            type=cast(ChatType, model.type),
            name=model.name,
            description=model.description,
            owner_id=model.owner_id,
            image_url=model.image_url,
            last_sequence=model.last_sequence,
            is_archived=model.is_archived,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ChatMemberDataMapper(DataMapper[ChatMemberOrm, ChatMember]):
    @staticmethod
    def to_entity(model: ChatMemberOrm) -> ChatMember:
        return ChatMember(
            id=model.id,
            chat_id=model.chat_id,
            user_id=model.user_id,
            role=cast(ChatMemberRole, model.role),
            last_read_seq=model.last_read_seq,
            joined_at=model.joined_at,
            left_at=model.left_at,
        )


class ChatSummaryDataMapper(DataMapper[Row[Any], ChatSummary]):
    @staticmethod
    def to_entity(row: Row[Any]) -> ChatSummary:
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
