from uuid import uuid4

import pytest

from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import (
    ChatCreate,
    ChatUpdateData,
    MemberCreate,
)
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import (
    CannotModifyPrivateChatError,
    NotChatOwnerError,
)
from src.modules.chats.usecases.update_chat import UpdateChatUseCase
from tests.unit.chats.fakes import FakeChatMemberRepository, FakeChatRepository


async def _make_group_chat(
    chats: FakeChatRepository, members: FakeChatMemberRepository, owner_id: object
) -> Chat:
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="Old Name")  # type: ignore[arg-type]
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]  # type: ignore[arg-type]
    )
    return chat


async def test_owner_can_rename_group_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = UpdateChatUseCase(chats, members)
    owner_id = uuid4()
    chat = await _make_group_chat(chats, members, owner_id)

    updated = await use_case(
        chat_id=chat.id,
        user_id=owner_id,
        update_data=ChatUpdateData(name="New Name"),
    )

    assert updated.name == "New Name"


async def test_non_owner_cannot_update() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = UpdateChatUseCase(chats, members)
    owner_id, other_id = uuid4(), uuid4()
    chat = await _make_group_chat(chats, members, owner_id)
    await members.add_members([MemberCreate(user_id=other_id, chat_id=chat.id)])

    with pytest.raises(NotChatOwnerError):
        await use_case(
            chat_id=chat.id,
            user_id=other_id,
            update_data=ChatUpdateData(name="New Name"),
        )


async def test_cannot_update_private_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    use_case = UpdateChatUseCase(chats, members)
    user_a, user_b = uuid4(), uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await members.add_members(
        [
            MemberCreate(user_id=user_a, chat_id=chat.id),
            MemberCreate(user_id=user_b, chat_id=chat.id),
        ]
    )

    with pytest.raises(CannotModifyPrivateChatError):
        await use_case(
            chat_id=chat.id,
            user_id=user_a,
            update_data=ChatUpdateData(name="New Name"),
        )
