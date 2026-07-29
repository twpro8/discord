from uuid import uuid4

from src.modules.chats.application.commands.create_chat import (
    CreateChatCommand,
    CreateChatCommandHandler,
)
from src.modules.chats.domain.entities.schemas import ChatCreate, ChatCreateRequest
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
)


def _handler() -> tuple[
    CreateChatCommandHandler, FakeChatRepository, FakeChatMemberRepository
]:
    chats = FakeChatRepository()
    members = FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    return CreateChatCommandHandler(uow), chats, members


async def test_self_chat_is_rejected() -> None:
    handler, _, members = _handler()
    user_id = uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=user_id,
            data=ChatCreateRequest(
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
    handler, _, members = _handler()
    creator_id, target_id = uuid4(), uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateRequest(
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


async def test_reuses_existing_private_chat_without_adding_members() -> None:
    handler, chats, members = _handler()
    creator_id, target_id = uuid4(), uuid4()
    existing = await chats.create(ChatCreate(type=ChatType.private))
    chats.seed_private_chat(creator_id, target_id, existing)

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateRequest(
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


async def test_creates_group_chat_with_owner_and_members() -> None:
    handler, _, members = _handler()
    creator_id, member_id = uuid4(), uuid4()

    result = await handler.handle(
        CreateChatCommand(
            creator_id=creator_id,
            data=ChatCreateRequest(
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
