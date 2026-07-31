from uuid import uuid4

from src.modules.chats.application.queries.list_members import (
    ListMembersQuery,
    ListMembersQueryHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import NotChatMemberError
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository


async def test_lists_active_members_oldest_first() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    handler = ListMembersQueryHandler(chats, members)
    owner_id, member_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    await members.add_members([MemberCreate(user_id=member_id, chat_id=chat.id)])

    result = await handler.handle(ListMembersQuery(chat_id=chat.id, user_id=owner_id))

    assert result.is_ok
    assert [m.user_id for m in result.value] == [owner_id, member_id]
    assert result.value[0].role == ChatMemberRole.owner


async def test_rejects_non_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    handler = ListMembersQueryHandler(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members([MemberCreate(user_id=owner_id, chat_id=chat.id)])

    result = await handler.handle(ListMembersQuery(chat_id=chat.id, user_id=uuid4()))

    assert result.is_err
    assert isinstance(result.error, NotChatMemberError)
