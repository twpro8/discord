from uuid import uuid4

from src.modules.chats.application.commands.leave_chat import (
    LeaveChatCommand,
    LeaveChatCommandHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import CannotLeavePrivateChatError
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
)


async def test_non_owner_member_can_leave() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = LeaveChatCommandHandler(uow)
    owner_id, member_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=member_id, chat_id=chat.id),
        ]
    )

    result = await handler.handle(LeaveChatCommand(chat_id=chat.id, user_id=member_id))

    assert result.is_ok
    assert await members.find_active(chat.id, member_id) is None
    assert chats.chats[chat.id].owner_id == owner_id
    assert chats.chats[chat.id].is_archived is False


async def test_owner_leaving_transfers_to_oldest_remaining_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = LeaveChatCommandHandler(uow)
    owner_id, oldest_id, newest_id = uuid4(), uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    await members.add_members([MemberCreate(user_id=oldest_id, chat_id=chat.id)])
    await members.add_members([MemberCreate(user_id=newest_id, chat_id=chat.id)])

    result = await handler.handle(LeaveChatCommand(chat_id=chat.id, user_id=owner_id))

    assert result.is_ok
    assert await members.find_active(chat.id, owner_id) is None
    assert chats.chats[chat.id].owner_id == oldest_id
    new_owner_membership = await members.find_active(chat.id, oldest_id)
    assert new_owner_membership is not None
    assert new_owner_membership.role == ChatMemberRole.owner
    assert chats.chats[chat.id].is_archived is False


async def test_owner_leaving_alone_archives_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = LeaveChatCommandHandler(uow)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )

    result = await handler.handle(LeaveChatCommand(chat_id=chat.id, user_id=owner_id))

    assert result.is_ok
    assert await members.find_active(chat.id, owner_id) is None
    assert chats.chats[chat.id].is_archived is True


async def test_cannot_leave_private_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = LeaveChatCommandHandler(uow)
    user_a, user_b = uuid4(), uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await members.add_members(
        [
            MemberCreate(user_id=user_a, chat_id=chat.id),
            MemberCreate(user_id=user_b, chat_id=chat.id),
        ]
    )

    result = await handler.handle(LeaveChatCommand(chat_id=chat.id, user_id=user_a))

    assert result.is_err
    assert isinstance(result.error, CannotLeavePrivateChatError)
