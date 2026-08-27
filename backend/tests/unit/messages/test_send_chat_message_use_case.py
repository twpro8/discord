from uuid import uuid4

import pytest

from src.core.realtime.envelope import EventType
from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.messages.domain.entities.dtos import MessageCreateData
from src.modules.messages.usecases.send_chat_message import SendChatMessageUseCase
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatsFacade,
)
from tests.unit.fakes import FakeTransaction
from tests.unit.messages.fakes import FakeMessageRepository, FakeRealtimeNotifier


def _use_case() -> tuple[
    SendChatMessageUseCase,
    FakeChatRepository,
    FakeChatMemberRepository,
    FakeRealtimeNotifier,
]:
    chats = FakeChatRepository()
    chat_members = FakeChatMemberRepository()
    chats_facade = FakeChatsFacade(chats, chat_members)
    realtime = FakeRealtimeNotifier()
    return (
        SendChatMessageUseCase(
            FakeTransaction(), FakeMessageRepository(), chats, chats_facade, realtime
        ),
        chats,
        chat_members,
        realtime,
    )


async def test_rejects_unknown_chat() -> None:
    use_case, _, _, _ = _use_case()

    with pytest.raises(ChatNotFoundError):
        await use_case(
            chat_id=uuid4(),
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )


async def test_rejects_non_member() -> None:
    use_case, chats, _, _ = _use_case()
    chat = await chats.create(ChatCreate(type=ChatType.private))

    with pytest.raises(NotChatMemberError):
        await use_case(
            chat_id=chat.id,
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )


async def test_success() -> None:
    use_case, chats, chat_members, realtime = _use_case()
    sender_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=sender_id, chat_id=chat.id)])

    message = await use_case(
        chat_id=chat.id,
        sender_id=sender_id,
        data=MessageCreateData(body="hello"),
    )

    assert message.body == "hello"
    assert message.chat_id == chat.id
    assert message.sequence == 1

    assert realtime.room_published == [
        (
            chat_room(chat.id),
            EventType.MESSAGE_CREATED,
            {
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
        )
    ]
