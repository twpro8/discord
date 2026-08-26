from uuid import uuid4

import pytest

from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatSummaryPage,
    GroupChatSummary,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatType
from src.modules.chats.domain.exceptions import ChatNotFoundError, NotChatMemberError
from src.modules.chats.usecases.get_chat_details import GetChatDetailsUseCase
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository


async def test_returns_summary_for_active_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = GetChatDetailsUseCase(chats, members)
    user_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=user_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=user_id, chat_id=chat.id)])
    summary = GroupChatSummary(
        id=chat.id,
        type=ChatType.group,
        name="G",
        image_url=None,
        unread_count=0,
        last_message=None,
    )
    chats.summary_page = ChatSummaryPage(items=[summary], next_cursor=None, total=1)

    result = await use_case(chat_id=chat.id, user_id=user_id)

    assert result is summary


async def test_returns_not_found_for_missing_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = GetChatDetailsUseCase(chats, members)

    with pytest.raises(ChatNotFoundError):
        await use_case(chat_id=uuid4(), user_id=uuid4())


async def test_returns_forbidden_for_non_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = GetChatDetailsUseCase(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    with pytest.raises(NotChatMemberError):
        await use_case(chat_id=chat.id, user_id=uuid4())
