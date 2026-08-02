from uuid import uuid4

from src.modules.chats.application.commands.create_chat import (
    CreateChatCommand,
    CreateChatCommandHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, ChatCreateData
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.events import ChatCreatedEvent
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
    RecordingEventBus,
)


def _handler() -> tuple[
    CreateChatCommandHandler,
    FakeChatRepository,
    FakeChatMemberRepository,
    RecordingEventBus,
]:
    chats = FakeChatRepository()
    members = FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    event_bus = RecordingEventBus()
    return CreateChatCommandHandler(uow, event_bus), chats, members, event_bus


async def test_self_chat_is_rejected() -> None:
    handler, _, members, _ = _handler()
    user_id = uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=user_id,
            data=ChatCreateData(
                type=ChatType.private,
                target_user_id=user_id,
                name=None,
                description=None,
            ),
        )
    )

    assert result.is_err
    assert isinstance(result.error, SelfChatForbiddenError)
    assert members.members == []


async def test_creates_private_chat_and_adds_both_members() -> None:
    handler, _, members, event_bus = _handler()
    creator_id, target_id = uuid4(), uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateData(
                type=ChatType.private,
                target_user_id=target_id,
                name=None,
                description=None,
            ),
        )
    )

    assert result.is_ok
    assert result.value.type == ChatType.private
    assert {m.user_id for m in members.members} == {creator_id, target_id}
    assert len(event_bus.published) == 1
    assert isinstance(event_bus.published[0], ChatCreatedEvent)
    assert event_bus.published[0].chat_id == result.value.id


async def test_reuses_existing_private_chat_without_adding_members() -> None:
    handler, chats, members, event_bus = _handler()
    creator_id, target_id = uuid4(), uuid4()
    existing = await chats.create(ChatCreate(type=ChatType.private))
    chats.seed_private_chat(creator_id, target_id, existing)

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateData(
                type=ChatType.private,
                target_user_id=target_id,
                name=None,
                description=None,
            ),
        )
    )

    assert result.is_ok
    assert result.value.id == existing.id
    assert members.members == []
    assert event_bus.published == []


async def test_creates_group_chat_with_owner_and_members() -> None:
    handler, _, members, event_bus = _handler()
    creator_id, member_id = uuid4(), uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateData(
                type=ChatType.group,
                name="Test Group",
                description=None,
                member_ids=[member_id],
            ),
        )
    )

    assert result.is_ok
    chat = result.value
    assert chat.type == ChatType.group
    assert chat.owner_id == creator_id

    roles = {m.user_id: m.role for m in members.members}
    assert roles[creator_id] == ChatMemberRole.owner
    assert roles[member_id] == ChatMemberRole.member

    assert len(event_bus.published) == 1
    assert isinstance(event_bus.published[0], ChatCreatedEvent)
