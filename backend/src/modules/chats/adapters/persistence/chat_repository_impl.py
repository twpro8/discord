from datetime import datetime
from uuid import UUID

from sqlalchemy import Executable, and_, desc, func, select, tuple_, update
from sqlalchemy.orm import aliased

from src.modules.chats.adapters.persistence.mappers import (
    ChatDataMapper,
    ChatSummaryDataMapper,
)
from src.modules.chats.adapters.persistence.models import ChatMemberOrm, ChatOrm
from src.modules.chats.domain.cursor import decode_cursor, encode_cursor
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatSummary,
    ChatSummaryPage,
    ChatUpdate,
)
from src.modules.chats.domain.enums import ChatType
from src.modules.messages.adapters.persistence.models import MessageOrm
from src.modules.users.adapters.persistence.models import UserOrm
from src.shared.adapters.base_repository import BaseRepository

SNIPPET_LEN = 120


class ChatRepositoryImpl(BaseRepository[ChatOrm, Chat, ChatCreate, ChatUpdate]):
    _model = ChatOrm
    _mapper = ChatDataMapper

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> Chat | None:
        """Find private chat between users"""

        member_a = aliased(ChatMemberOrm)
        member_b = aliased(ChatMemberOrm)

        query = (
            select(ChatOrm)
            .join(
                member_a,
                and_(member_a.chat_id == ChatOrm.id, member_a.user_id == user_a),
            )
            .join(
                member_b,
                and_(member_b.chat_id == ChatOrm.id, member_b.user_id == user_b),
            )
            .where(ChatOrm.type == ChatType.private)
        )
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return ChatDataMapper.to_entity(model) if model else None

    async def list_chats_for_user(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage:
        decoded_cursor = decode_cursor(cursor) if cursor else None

        query = self._build_chat_list_query(user_id, limit, decoded_cursor)
        rows = (await self._session.execute(query)).all()

        has_next = len(rows) > limit
        rows = rows[:limit]

        items = [ChatSummaryDataMapper.to_entity(r) for r in rows]
        next_cursor = (
            encode_cursor(rows[-1].sort_key, rows[-1].id) if has_next else None
        )
        total = await self._count_chats(user_id)

        return ChatSummaryPage(items=items, next_cursor=next_cursor, total=total)

    async def _count_chats(self, user_id: UUID) -> int:
        query = (
            select(func.count())
            .select_from(ChatOrm)
            .join(ChatMemberOrm, ChatMemberOrm.chat_id == ChatOrm.id)
            .where(ChatMemberOrm.user_id == user_id, ChatMemberOrm.left_at.is_(None))
        )
        result = await self._session.execute(query)
        count = result.scalar_one()
        return count

    @staticmethod
    def _build_chat_list_query(
        user_id: UUID,
        limit: int,
        cursor: tuple[datetime, UUID] | None,
        chat_id: UUID | None = None,
    ) -> Executable:
        my_membership = aliased(ChatMemberOrm)

        last_message_sq = (
            select(
                MessageOrm.chat_id,
                MessageOrm.sender_id,
                func.left(MessageOrm.body, SNIPPET_LEN).label("body_snippet"),
                MessageOrm.created_at,
            )
            .where(MessageOrm.chat_id.is_not(None), MessageOrm.is_deleted.is_(False))
            .distinct(MessageOrm.chat_id)
            .order_by(MessageOrm.chat_id, MessageOrm.sequence.desc())
            .subquery("last_message")
        )

        peer_sq = (
            select(
                ChatMemberOrm.chat_id,
                ChatMemberOrm.user_id.label("peer_id"),
                UserOrm.name.label("peer_name"),
                UserOrm.avatar_url.label("peer_avatar_url"),
            )
            .join(UserOrm, UserOrm.id == ChatMemberOrm.user_id)
            .where(
                ChatMemberOrm.user_id != user_id,
                ChatMemberOrm.left_at.is_(None),
            )
            .distinct(ChatMemberOrm.chat_id)
            .order_by(ChatMemberOrm.chat_id, ChatMemberOrm.joined_at)
            .subquery("peer")
        )

        unread_count_sq = (
            select(func.count(MessageOrm.id))
            .where(
                MessageOrm.chat_id == ChatOrm.id,
                MessageOrm.is_deleted.is_(False),
                MessageOrm.sequence > my_membership.last_read_seq,
            )
            .correlate(ChatOrm, my_membership)
            .scalar_subquery()
        )

        sort_key = func.coalesce(last_message_sq.c.created_at, ChatOrm.created_at)
        base_filters = (
            my_membership.user_id == user_id,
            my_membership.left_at.is_(None),
        )

        query = (
            select(
                ChatOrm.id,
                ChatOrm.type,
                ChatOrm.name,
                ChatOrm.image_url,
                unread_count_sq.label("unread_count"),
                last_message_sq.c.sender_id.label("lm_sender_id"),
                last_message_sq.c.body_snippet.label("lm_body_snippet"),
                last_message_sq.c.created_at.label("lm_created_at"),
                peer_sq.c.peer_id,
                peer_sq.c.peer_name,
                peer_sq.c.peer_avatar_url,
                sort_key.label("sort_key"),
            )
            .join(my_membership, my_membership.chat_id == ChatOrm.id)
            .outerjoin(last_message_sq, last_message_sq.c.chat_id == ChatOrm.id)
            .outerjoin(peer_sq, peer_sq.c.chat_id == ChatOrm.id)
            .where(*base_filters)
            .order_by(desc(sort_key), desc(ChatOrm.id))
            .limit(limit + 1)
        )

        if chat_id is not None:
            query = query.where(ChatOrm.id == chat_id)

        if cursor is not None:
            cursor_ts, cursor_id = cursor
            query = query.where(tuple_(sort_key, ChatOrm.id) < (cursor_ts, cursor_id))

        return query

    async def increment_sequence(self, chat_id: UUID) -> int:
        stmt = (
            update(ChatOrm)
            .where(ChatOrm.id == chat_id)
            .values(last_sequence=ChatOrm.last_sequence + 1)
            .returning(ChatOrm.last_sequence)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_summary_for_user(
        self, chat_id: UUID, user_id: UUID
    ) -> ChatSummary | None:
        query = self._build_chat_list_query(
            user_id, limit=1, cursor=None, chat_id=chat_id
        )
        row = (await self._session.execute(query)).first()
        return ChatSummaryDataMapper.to_entity(row) if row else None
