from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, insert, select, func, desc, tuple_, Executable
from sqlalchemy.orm import aliased

from src.chat.cursor import encode_cursor, decode_cursor
from src.core.repositories.base_repository import BaseRepository
from src.chat.models import ChatOrm, ChatMemberOrm
from src.chat.schemas import (
    Chat,
    ChatMember,
    MemberCreate,
    ChatSummaryPage,
)
from src.chat.mappers import ChatMapper, MemberMapper, ChatSummaryMapper
from src.chat.enums import ChatType
from src.message.models import MessageOrm

SNIPPET_LEN = 120


class ChatRepository(BaseRepository[ChatOrm, Chat]):
    model = ChatOrm
    mapper = ChatMapper

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> Chat | None:
        """Find private chat beetween users"""

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

        return await self._execute_and_map_one_or_none(query)

    async def list_chats_for_user(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage:
        decoded_cursor = decode_cursor(cursor) if cursor else None

        query = self._build_chat_list_query(user_id, limit, decoded_cursor)
        rows = (await self.session.execute(query)).all()

        has_next = len(rows) > limit
        rows = rows[:limit]

        items = [ChatSummaryMapper.to_schema(r) for r in rows]
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
        result = await self.session.execute(query)
        count = result.scalar_one()
        return count

    @staticmethod
    def _build_chat_list_query(
        user_id: UUID,
        limit: int,
        cursor: tuple[datetime, UUID] | None,
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
                sort_key.label("sort_key"),
            )
            .join(my_membership, my_membership.chat_id == ChatOrm.id)
            .outerjoin(last_message_sq, last_message_sq.c.chat_id == ChatOrm.id)
            .where(*base_filters)
            .order_by(desc(sort_key), desc(ChatOrm.id))
            .limit(limit + 1)
        )

        if cursor is not None:
            cursor_ts, cursor_id = cursor
            query = query.where(tuple_(sort_key, ChatOrm.id) < (cursor_ts, cursor_id))

        return query


class MemberRepository(BaseRepository[ChatMemberOrm, ChatMember]):
    model = ChatMemberOrm
    mapper = MemberMapper

    async def add_members(self, members: list[MemberCreate]) -> None:
        statement = insert(ChatMemberOrm).values([m.model_dump() for m in members])
        await self.session.execute(statement)
