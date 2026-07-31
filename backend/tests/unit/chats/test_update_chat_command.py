from uuid import uuid4

from src.modules.chats.application.commands.update_chat import (
    UpdateChatCommand,
    UpdateChatCommandHandler,
)
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
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
)


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
    uow = FakeChatUnitOfWork(chats, members)
    handler = UpdateChatCommandHandler(uow)
    owner_id = uuid4()
    chat = await _make_group_chat(chats, members, owner_id)

    result = await handler.handle(
        UpdateChatCommand(
            chat_id=chat.id,
            user_id=owner_id,
            update_data=ChatUpdateData(name="New Name"),
        )
    )

    assert result.is_ok
    assert result.value.name == "New Name"
    assert uow.committed


async def test_non_owner_cannot_update() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = UpdateChatCommandHandler(uow)
    owner_id, other_id = uuid4(), uuid4()
    chat = await _make_group_chat(chats, members, owner_id)
    await members.add_members([MemberCreate(user_id=other_id, chat_id=chat.id)])

    result = await handler.handle(
        UpdateChatCommand(
            chat_id=chat.id,
            user_id=other_id,
            update_data=ChatUpdateData(name="New Name"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotChatOwnerError)


async def test_cannot_update_private_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    handler = UpdateChatCommandHandler(uow)
    user_a, user_b = uuid4(), uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await members.add_members(
        [
            MemberCreate(user_id=user_a, chat_id=chat.id),
            MemberCreate(user_id=user_b, chat_id=chat.id),
        ]
    )

    result = await handler.handle(
        UpdateChatCommand(
            chat_id=chat.id,
            user_id=user_a,
            update_data=ChatUpdateData(name="New Name"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, CannotModifyPrivateChatError)
