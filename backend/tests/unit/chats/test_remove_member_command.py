from uuid import uuid4

from src.core.realtime.rooms import chat_room
from src.modules.chats.application.commands.remove_member import (
    RemoveMemberCommand,
    RemoveMemberCommandHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import (
    CannotRemoveSelfError,
    MemberNotFoundError,
    NotChatOwnerError,
)
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
    FakeRoomMembershipUpdater,
)


async def test_owner_can_remove_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    room_updater = FakeRoomMembershipUpdater()
    handler = RemoveMemberCommandHandler(uow, room_updater)
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

    result = await handler.handle(
        RemoveMemberCommand(chat_id=chat.id, user_id=owner_id, target_user_id=target_id)
    )

    assert result.is_ok
    assert await members.find_active(chat.id, target_id) is None
    assert uow.committed
    assert room_updater.left == [(target_id, chat_room(chat.id))]


async def test_owner_cannot_remove_self() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = RemoveMemberCommandHandler(uow, FakeRoomMembershipUpdater())
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )

    result = await handler.handle(
        RemoveMemberCommand(chat_id=chat.id, user_id=owner_id, target_user_id=owner_id)
    )

    assert result.is_err
    assert isinstance(result.error, CannotRemoveSelfError)


async def test_removing_nonmember_fails() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = RemoveMemberCommandHandler(uow, FakeRoomMembershipUpdater())
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )

    result = await handler.handle(
        RemoveMemberCommand(chat_id=chat.id, user_id=owner_id, target_user_id=uuid4())
    )

    assert result.is_err
    assert isinstance(result.error, MemberNotFoundError)


async def test_non_owner_cannot_remove_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = RemoveMemberCommandHandler(uow, FakeRoomMembershipUpdater())
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

    result = await handler.handle(
        RemoveMemberCommand(chat_id=chat.id, user_id=other_id, target_user_id=target_id)
    )

    assert result.is_err
    assert isinstance(result.error, NotChatOwnerError)
