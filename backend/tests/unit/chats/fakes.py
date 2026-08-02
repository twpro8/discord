from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.event_bus import EventHandler
from src.modules.chats.domain import services as chat_permission_services
from src.modules.chats.domain.entities.chat import Chat, ChatMember
from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatMemberSummary,
    ChatSummary,
    ChatSummaryPage,
    ChatUpdate,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.domain.domain_event import DomainEvent
from src.shared.domain.unset import set_fields


class FakeChatRepository:
    def __init__(self) -> None:
        self.chats: dict[UUID, Chat] = {}
        self._private_chats: dict[frozenset[UUID], Chat] = {}
        self.summary_page = ChatSummaryPage(items=[], next_cursor=None, total=0)

    def seed_private_chat(self, user_a: UUID, user_b: UUID, chat: Chat) -> None:
        self._private_chats[frozenset({user_a, user_b})] = chat

    async def create(self, data: ChatCreate) -> Chat:
        now = datetime.now(UTC)
        chat = Chat(
            id=uuid4(),
            type=data.type,
            name=data.name,
            description=data.description,
            owner_id=data.owner_id,
            image_url=None,
            last_sequence=0,
            is_archived=False,
            created_at=now,
            updated_at=now,
        )
        self.chats[chat.id] = chat
        return chat

    async def find_by_id(self, chat_id: UUID) -> Chat | None:
        return self.chats.get(chat_id)

    async def find_private_chat(self, user_a: UUID, user_b: UUID) -> Chat | None:
        return self._private_chats.get(frozenset({user_a, user_b}))

    async def increment_sequence(self, chat_id: UUID) -> int:
        chat = self.chats[chat_id]
        chat.last_sequence += 1
        return chat.last_sequence

    async def list_chats_for_user(
        self,
        user_id: UUID,
        limit: int,
        cursor: str | None,
    ) -> ChatSummaryPage:
        return self.summary_page

    async def update(self, chat_id: UUID, data: ChatUpdate) -> Chat:
        chat = self.chats[chat_id]
        for key, value in set_fields(data).items():
            setattr(chat, key, value)
        chat.updated_at = datetime.now(UTC)
        return chat

    async def get_summary_for_user(
        self, chat_id: UUID, user_id: UUID
    ) -> ChatSummary | None:
        return next((s for s in self.summary_page.items if s.id == chat_id), None)


class FakeChatMemberRepository:
    def __init__(self) -> None:
        self.members: list[ChatMember] = []

    async def add_members(self, members: list[MemberCreate]) -> None:
        now = datetime.now(UTC)
        for member in members:
            self.members.append(
                ChatMember(
                    id=uuid4(),
                    chat_id=member.chat_id,
                    user_id=member.user_id,
                    role=member.role or ChatMemberRole.member,
                    last_read_seq=0,
                    joined_at=now,
                    left_at=None,
                )
            )

    async def find_active(self, chat_id: UUID, user_id: UUID) -> ChatMember | None:
        for member in self.members:
            if (
                member.chat_id == chat_id
                and member.user_id == user_id
                and member.left_at is None
            ):
                return member
        return None

    def _active_in_chat(self, chat_id: UUID) -> list[ChatMember]:
        return [m for m in self.members if m.chat_id == chat_id and m.left_at is None]

    async def list_active_with_user(self, chat_id: UUID) -> list[ChatMemberSummary]:
        return [
            ChatMemberSummary(
                user_id=m.user_id,
                username=str(m.user_id),
                display_name=str(m.user_id),
                avatar_url=None,
                role=m.role,
                joined_at=m.joined_at,
            )
            for m in sorted(self._active_in_chat(chat_id), key=lambda m: m.joined_at)
        ]

    async def list_active_user_ids(self, chat_id: UUID) -> set[UUID]:
        return {m.user_id for m in self._active_in_chat(chat_id)}

    async def remove(self, chat_id: UUID, user_id: UUID) -> None:
        self.members = [
            m
            for m in self.members
            if not (m.chat_id == chat_id and m.user_id == user_id)
        ]

    async def count_active(self, chat_id: UUID) -> int:
        return len(self._active_in_chat(chat_id))

    async def find_oldest_active_excluding(
        self, chat_id: UUID, exclude_user_id: UUID
    ) -> ChatMember | None:
        candidates = [
            m for m in self._active_in_chat(chat_id) if m.user_id != exclude_user_id
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda m: m.joined_at)

    async def update_role(self, member_id: UUID, role: ChatMemberRole) -> None:
        for member in self.members:
            if member.id == member_id:
                member.role = role
                return

    async def update_last_read_seq(
        self, chat_id: UUID, user_id: UUID, up_to_seq: int
    ) -> None:
        for member in self.members:
            if member.chat_id == chat_id and member.user_id == user_id:
                member.last_read_seq = max(member.last_read_seq, up_to_seq)
                return


class FakeChatUnitOfWork(ChatUnitOfWork):
    def __init__(
        self,
        chats: FakeChatRepository,
        members: FakeChatMemberRepository,
    ) -> None:
        self.chats = chats
        self.members = members
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeChatsFacade:
    def __init__(
        self,
        chats: FakeChatRepository,
        chat_members: FakeChatMemberRepository,
    ) -> None:
        self._chats = chats
        self._chat_members = chat_members

    async def assert_is_chat_member(self, user_id: UUID, chat_id: UUID) -> None:
        await chat_permission_services.assert_is_chat_member(
            self._chats, self._chat_members, user_id, chat_id
        )

    async def assert_is_chat_owner(self, user_id: UUID, chat_id: UUID) -> None:
        await chat_permission_services.assert_is_chat_owner(
            self._chats, self._chat_members, user_id, chat_id
        )

    async def list_active_user_ids(self, chat_id: UUID) -> set[UUID]:
        return await self._chat_members.list_active_user_ids(chat_id)


class RecordingEventBus:
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        pass

    async def publish(self, event: DomainEvent) -> None:
        self.published.append(event)

    async def publish_many(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            await self.publish(event)
