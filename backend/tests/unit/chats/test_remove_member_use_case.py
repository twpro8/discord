from uuid import uuid4

import pytest

from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import (
    CannotRemoveSelfError,
    MemberNotFoundError,
    NotChatOwnerError,
)
from src.modules.chats.usecases.remove_member import RemoveMemberUseCase
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeRoomMembershipUpdater,
)
from tests.unit.fakes import FakeTransaction


async def test_owner_can_remove_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    tx = FakeTransaction()
    room_updater = FakeRoomMembershipUpdater()
    use_case = RemoveMemberUseCase(tx, chats, members, room_updater)
    owner_id, target_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=target_id, chat_id=chat.id),
        ]
    )

    await use_case(chat_id=chat.id, user_id=owner_id, target_user_id=target_id)

    assert await members.find_active(chat.id, target_id) is None
    assert tx.committed
    assert room_updater.left == [(target_id, chat_room(chat.id))]


async def test_owner_cannot_remove_self() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = RemoveMemberUseCase(
        FakeTransaction(), chats, members, FakeRoomMembershipUpdater()
    )
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )

    with pytest.raises(CannotRemoveSelfError):
        await use_case(chat_id=chat.id, user_id=owner_id, target_user_id=owner_id)


async def test_removing_nonmember_fails() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = RemoveMemberUseCase(
        FakeTransaction(), chats, members, FakeRoomMembershipUpdater()
    )
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )

    with pytest.raises(MemberNotFoundError):
        await use_case(chat_id=chat.id, user_id=owner_id, target_user_id=uuid4())


async def test_non_owner_cannot_remove_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = RemoveMemberUseCase(
        FakeTransaction(), chats, members, FakeRoomMembershipUpdater()
    )
    owner_id, other_id, target_id = uuid4(), uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=other_id, chat_id=chat.id),
            MemberCreate(user_id=target_id, chat_id=chat.id),
        ]
    )

    with pytest.raises(NotChatOwnerError):
        await use_case(chat_id=chat.id, user_id=other_id, target_user_id=target_id)
