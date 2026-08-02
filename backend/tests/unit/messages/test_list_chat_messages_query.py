from uuid import uuid4

from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from src.modules.messages.application.queries.list_chat_messages import (
    ListChatMessagesQuery,
    ListChatMessagesQueryHandler,
)
from src.modules.messages.domain.entities.dtos import MessageCreate
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatsFacade,
)
from tests.unit.messages.fakes import FakeMessageRepository


async def test_returns_messages_in_ascending_order() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    messages = FakeMessageRepository()
    chats_facade = FakeChatsFacade(chats, chat_members)
    handler = ListChatMessagesQueryHandler(messages, chats_facade)

    user_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])
    for seq in (1, 2, 3):
        await messages.create(
            MessageCreate(
                sender_id=user_id,
                body=f"msg{seq}",
                sequence=seq,
                parent_id=None,
                chat_id=chat.id,
            )
        )

    result = await handler.handle(
        ListChatMessagesQuery(chat_id=chat.id, user_id=user_id, limit=20)
    )

    assert result.is_ok
    assert [m.sequence for m in result.value.items] == [1, 2, 3]


async def test_rejects_non_member() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    messages = FakeMessageRepository()
    chats_facade = FakeChatsFacade(chats, chat_members)
    handler = ListChatMessagesQueryHandler(messages, chats_facade)

    owner_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    result = await handler.handle(
        ListChatMessagesQuery(chat_id=chat.id, user_id=uuid4(), limit=20)
    )

    assert result.is_err
    assert isinstance(result.error, NotChatMemberError)
