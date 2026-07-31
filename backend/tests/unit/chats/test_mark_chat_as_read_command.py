from uuid import uuid4

from src.modules.chats.application.commands.mark_chat_as_read import (
    MarkChatAsReadCommand,
    MarkChatAsReadCommandHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
)


async def test_marks_read_up_to_latest_sequence_by_default() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = MarkChatAsReadCommandHandler(uow)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    chat.last_sequence = 5
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])

    result = await handler.handle(
        MarkChatAsReadCommand(chat_id=chat.id, user_id=user_id, up_to_sequence=None)
    )

    assert result.is_ok
    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 5
    assert uow.committed


async def test_marks_read_up_to_explicit_sequence() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = MarkChatAsReadCommandHandler(uow)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    chat.last_sequence = 10
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])

    result = await handler.handle(
        MarkChatAsReadCommand(chat_id=chat.id, user_id=user_id, up_to_sequence=3)
    )

    assert result.is_ok
    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 3


async def test_cursor_never_regresses() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = MarkChatAsReadCommandHandler(uow)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])
    await handler.handle(
        MarkChatAsReadCommand(chat_id=chat.id, user_id=user_id, up_to_sequence=10)
    )

    result = await handler.handle(
        MarkChatAsReadCommand(chat_id=chat.id, user_id=user_id, up_to_sequence=3)
    )

    assert result.is_ok
    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 10


async def test_rejects_non_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = MarkChatAsReadCommandHandler(uow)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    result = await handler.handle(
        MarkChatAsReadCommand(chat_id=chat.id, user_id=uuid4(), up_to_sequence=None)
    )

    assert result.is_err
    assert isinstance(result.error, NotChatMemberError)
