from uuid import uuid4

import pytest

from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from src.modules.chats.usecases.mark_chat_as_read import MarkChatAsReadUseCase
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository


async def test_marks_read_up_to_latest_sequence_by_default() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = MarkChatAsReadUseCase(chats, members)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    chat.last_sequence = 5
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])

    await use_case(chat_id=chat.id, user_id=user_id, up_to_sequence=None)

    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 5


async def test_marks_read_up_to_explicit_sequence() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = MarkChatAsReadUseCase(chats, members)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    chat.last_sequence = 10
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])

    await use_case(chat_id=chat.id, user_id=user_id, up_to_sequence=3)

    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 3


async def test_cursor_never_regresses() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = MarkChatAsReadUseCase(chats, members)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])
    await use_case(chat_id=chat.id, user_id=user_id, up_to_sequence=10)

    await use_case(chat_id=chat.id, user_id=user_id, up_to_sequence=3)

    membership = await members.find_active(chat.id, user_id)
    assert membership is not None
    assert membership.last_read_seq == 10


async def test_rejects_non_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = MarkChatAsReadUseCase(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    with pytest.raises(NotChatMemberError):
        await use_case(chat_id=chat.id, user_id=uuid4(), up_to_sequence=None)
