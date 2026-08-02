from uuid import uuid4

from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
    SendChatMessageCommandHandler,
)
from src.modules.messages.domain.entities.dtos import MessageCreateData
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatsFacade,
)
from tests.unit.messages.fakes import (
    FakeMessageRepository,
    FakeMessageUnitOfWork,
    FakeRealtimeNotifier,
)


def _handler() -> tuple[
    SendChatMessageCommandHandler,
    FakeChatRepository,
    FakeChatMemberRepository,
    FakeRealtimeNotifier,
]:
    chats = FakeChatRepository()
    chat_members = FakeChatMemberRepository()
    uow = FakeMessageUnitOfWork(
        FakeMessageRepository(),
        chats,
        FakeChannelRepository(),
    )
    chats_facade = FakeChatsFacade(chats, chat_members)
    realtime = FakeRealtimeNotifier()
    return (
        SendChatMessageCommandHandler(uow, chats_facade, realtime),
        chats,
        chat_members,
        realtime,
    )


async def test_rejects_unknown_chat() -> None:
    handler, _, _, _ = _handler()

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=uuid4(),
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChatNotFoundError)


async def test_rejects_non_member() -> None:
    handler, chats, _, _ = _handler()
    chat = await chats.create(ChatCreate(type=ChatType.private))

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=chat.id,
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotChatMemberError)


async def test_success() -> None:
    handler, chats, chat_members, realtime = _handler()
    sender_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=sender_id, chat_id=chat.id)])

    result = await handler.handle(
        SendChatMessageCommand(
            chat_id=chat.id,
            sender_id=sender_id,
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_ok
    message = result.value
    assert message.body == "hello"
    assert message.chat_id == chat.id
    assert message.sequence == 1

    assert realtime.published == [
        (
            sender_id,
            {
                "type": "message.created",
                "payload": {
                    "id": message.id,
                    "sender_id": message.sender_id,
                    "body": message.body,
                    "sequence": message.sequence,
                    "parent_id": message.parent_id,
                    "is_edited": message.is_edited,
                    "is_deleted": message.is_deleted,
                    "deleted_at": message.deleted_at,
                    "created_at": message.created_at,
                    "updated_at": message.updated_at,
                    "chat_id": message.chat_id,
                },
            },
        )
    ]
