from uuid import uuid4

import pytest

from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from src.modules.chats.usecases.list_members import ListMembersUseCase
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository


async def test_lists_active_members_oldest_first() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = ListMembersUseCase(chats, members)
    owner_id, member_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    await members.add_members([MemberCreate(user_id=member_id, chat_id=chat.id)])

    result = await use_case(chat_id=chat.id, user_id=owner_id)

    assert [m.user_id for m in result] == [owner_id, member_id]
    assert result[0].role == ChatMemberRole.owner


async def test_rejects_non_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = ListMembersUseCase(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    with pytest.raises(NotChatMemberError):
        await use_case(chat_id=chat.id, user_id=uuid4())
