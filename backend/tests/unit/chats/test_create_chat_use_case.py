from uuid import uuid4

import pytest

from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.entities.dtos import ChatCreate, ChatCreateData
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import SelfChatForbiddenError
from src.modules.chats.usecases.create_chat import CreateChatUseCase
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeRoomMembershipUpdater,
)
from tests.unit.fakes import FakeTransaction


def _use_case() -> tuple[
    CreateChatUseCase,
    FakeChatRepository,
    FakeChatMemberRepository,
    FakeRoomMembershipUpdater,
]:
    chats = FakeChatRepository()
    members = FakeChatMemberRepository()
    room_updater = FakeRoomMembershipUpdater()
    return (
        CreateChatUseCase(FakeTransaction(), chats, members, room_updater),
        chats,
        members,
        room_updater,
    )


async def test_self_chat_is_rejected() -> None:
    use_case, _, members, _ = _use_case()
    user_id = uuid4()

    with pytest.raises(SelfChatForbiddenError):
        await use_case(
            creator_id=user_id,
            data=ChatCreateData(
                type=ChatType.private,
                target_user_id=user_id,
                name=None,
                description=None,
            ),
        )

    assert members.members == []


async def test_creates_private_chat_and_adds_both_members() -> None:
    use_case, _, members, room_updater = _use_case()
    creator_id, target_id = uuid4(), uuid4()

    chat = await use_case(
        creator_id=creator_id,
        data=ChatCreateData(
            type=ChatType.private,
            target_user_id=target_id,
            name=None,
            description=None,
        ),
    )

    assert chat.type == ChatType.private
    assert {m.user_id for m in members.members} == {creator_id, target_id}

    room = chat_room(chat.id)
    assert set(room_updater.joined) == {(creator_id, room), (target_id, room)}


async def test_reuses_existing_private_chat_without_adding_members() -> None:
    use_case, chats, members, room_updater = _use_case()
    creator_id, target_id = uuid4(), uuid4()
    existing = await chats.create(ChatCreate(type=ChatType.private))
    chats.seed_private_chat(creator_id, target_id, existing)

    chat = await use_case(
        creator_id=creator_id,
        data=ChatCreateData(
            type=ChatType.private,
            target_user_id=target_id,
            name=None,
            description=None,
        ),
    )

    assert chat.id == existing.id
    assert members.members == []
    assert room_updater.joined == []


async def test_creates_group_chat_with_owner_and_members() -> None:
    use_case, _, members, room_updater = _use_case()
    creator_id, member_id = uuid4(), uuid4()

    chat = await use_case(
        creator_id=creator_id,
        data=ChatCreateData(
            type=ChatType.group,
            name="Test Group",
            description=None,
            member_ids=[member_id],
        ),
    )

    assert chat.type == ChatType.group
    assert chat.owner_id == creator_id

    roles = {m.user_id: m.role for m in members.members}
    assert roles[creator_id] == ChatMemberRole.owner
    assert roles[member_id] == ChatMemberRole.member

    room = chat_room(chat.id)
    assert set(room_updater.joined) == {(creator_id, room), (member_id, room)}
