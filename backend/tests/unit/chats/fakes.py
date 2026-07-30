from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.event_bus import EventHandler
from src.modules.chats.domain import services as chat_permission_services
from src.modules.chats.domain.entities.chat import Chat, ChatMember
from src.modules.chats.domain.entities.schemas import (
    ChatCreate,
    ChatSummaryPage,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork
from src.shared.domain.domain_event import DomainEvent


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
