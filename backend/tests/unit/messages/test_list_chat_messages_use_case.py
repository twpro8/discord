from uuid import uuid4

import pytest

from src.core.realtime.rooms import chat_room
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from src.modules.messages.domain.entities.dtos import MessageCreate
from src.modules.messages.usecases.list_chat_messages import ListChatMessagesUseCase
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatsFacade,
    FakeRoomMembershipUpdater,
)
from tests.unit.messages.fakes import FakeMessageRepository


async def test_returns_messages_in_ascending_order() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    messages = FakeMessageRepository()
    chats_facade = FakeChatsFacade(chats, chat_members)
    room_membership_updater = FakeRoomMembershipUpdater()
    use_case = ListChatMessagesUseCase(messages, chats_facade, room_membership_updater)

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

    page = await use_case(chat_id=chat.id, user_id=user_id, limit=20)

    assert [m.sequence for m in page.items] == [1, 2, 3]
    assert room_membership_updater.joined == [(user_id, chat_room(chat.id))]


async def test_rejects_non_member() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    messages = FakeMessageRepository()
    chats_facade = FakeChatsFacade(chats, chat_members)
    room_membership_updater = FakeRoomMembershipUpdater()
    use_case = ListChatMessagesUseCase(messages, chats_facade, room_membership_updater)

    owner_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await chat_members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    with pytest.raises(NotChatMemberError):
        await use_case(chat_id=chat.id, user_id=uuid4(), limit=20)

    # Non-members are rejected before the join-side-effect runs.
    assert room_membership_updater.joined == []
