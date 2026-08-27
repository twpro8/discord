from uuid import uuid4

import pytest

from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import (
    CannotModifyPrivateChatError,
    NotChatOwnerError,
    TargetUserNotFoundError,
)
from src.modules.chats.usecases.add_member import AddMemberUseCase
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
    FakeRoomMembershipUpdater,
)
from tests.unit.friends.fakes import FakeUsersFacade
from tests.unit.users.fakes import make_user


async def test_owner_can_add_existing_and_skip_already_members() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    existing_user = make_user(username="bob")
    await members.add_members([MemberCreate(user_id=existing_user.id, chat_id=chat.id)])

    new_user = make_user()
    users_facade = FakeUsersFacade([new_user, existing_user])
    room_updater = FakeRoomMembershipUpdater()
    use_case = AddMemberUseCase(uow, users_facade, room_updater)

    result = await use_case(
        chat_id=chat.id,
        user_id=owner_id,
        user_ids=[new_user.id, existing_user.id],
    )

    assert result.added == [new_user.id]
    assert result.skipped == [existing_user.id]
    assert uow.committed
    # Only the newly-added member is joined — the already-active one is
    # skipped, so its (presumably already-joined) room membership is left
    # untouched.
    assert room_updater.joined == [(new_user.id, chat_room(chat.id))]


async def test_rejects_nonexistent_target_user() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    users_facade = FakeUsersFacade([])
    use_case = AddMemberUseCase(uow, users_facade, FakeRoomMembershipUpdater())

    with pytest.raises(TargetUserNotFoundError):
        await use_case(chat_id=chat.id, user_id=owner_id, user_ids=[uuid4()])


async def test_non_owner_cannot_add_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id, other_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=other_id, chat_id=chat.id),
        ]
    )
    users_facade = FakeUsersFacade([])
    use_case = AddMemberUseCase(uow, users_facade, FakeRoomMembershipUpdater())

    with pytest.raises(NotChatOwnerError):
        await use_case(chat_id=chat.id, user_id=other_id, user_ids=[uuid4()])


async def test_cannot_add_member_to_private_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    user_a, user_b = uuid4(), uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await members.add_members(
        [
            MemberCreate(user_id=user_a, chat_id=chat.id),
            MemberCreate(user_id=user_b, chat_id=chat.id),
        ]
    )
    users_facade = FakeUsersFacade([])
    use_case = AddMemberUseCase(uow, users_facade, FakeRoomMembershipUpdater())

    with pytest.raises(CannotModifyPrivateChatError):
        await use_case(chat_id=chat.id, user_id=user_a, user_ids=[uuid4()])
