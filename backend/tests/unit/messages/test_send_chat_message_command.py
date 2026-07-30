from uuid import uuid4

from src.modules.chats.domain.entities.schemas import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
    SendChatMessageCommandHandler,
)
from src.modules.messages.domain.entities.schemas import MessageCreateRequest
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository
from tests.unit.messages.fakes import FakeMessageRepository, FakeMessageUnitOfWork
from tests.unit.servers.fakes import FakeServerMemberRepository


def _handler() -> tuple[
    SendChatMessageCommandHandler, FakeChatRepository, FakeChatMemberRepository
]:
    chats = FakeChatRepository()
    chat_members = FakeChatMemberRepository()
    uow = FakeMessageUnitOfWork(
        FakeMessageRepository(),
        chats,
        chat_members,
        FakeChannelRepository(),
        FakeServerMemberRepository(),
    )
    return SendChatMessageCommandHandler(uow), chats, chat_members


async def test_rejects_unknown_chat() -> None:
    handler, _, _ = _handler()

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=uuid4(),
            sender_id=uuid4(),
            data=MessageCreateRequest(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChatNotFoundError)


async def test_rejects_non_member() -> None:
    handler, chats, _ = _handler()
    chat = await chats.create(ChatCreate(type=ChatType.private))

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=chat.id,
            sender_id=uuid4(),
            data=MessageCreateRequest(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotChatMemberError)


async def test_success() -> None:
    handler, chats, chat_members = _handler()
    sender_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=sender_id, chat_id=chat.id)])

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=chat.id,
            sender_id=sender_id,
            data=MessageCreateRequest(body="hello"),
        )
    )

    assert result.is_ok
    message = result.value
    assert message.body == "hello"
    assert message.chat_id == chat.id
    assert message.sequence == 1
