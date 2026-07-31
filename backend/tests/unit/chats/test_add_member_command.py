from uuid import uuid4

from src.modules.chats.application.commands.add_member import (
    AddMemberCommand,
    AddMemberCommandHandler,
)
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.chats.domain.exceptions import (
    CannotModifyPrivateChatError,
    NotChatOwnerError,
    TargetUserNotFoundError,
)
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatUnitOfWork,
)
from tests.unit.friends.fakes import FakeUsersFacade
from tests.unit.users.fakes import make_user


async def test_owner_can_add_existing_and_skip_already_members() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    existing_user = make_user(username="bob")
    await members.add_members([MemberCreate(user_id=existing_user.id, chat_id=chat.id)])

    new_user = make_user()
    users_facade = FakeUsersFacade([new_user, existing_user])
    handler = AddMemberCommandHandler(uow, users_facade)

    result = await handler.handle(
        AddMemberCommand(
            chat_id=chat.id,
            user_id=owner_id,
            user_ids=[new_user.id, existing_user.id],
        )
    )

    assert result.is_ok
    assert result.value.added == [new_user.id]
    assert result.value.skipped == [existing_user.id]
    assert uow.committed


async def test_rejects_nonexistent_target_user() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id = uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner)]
    )
    users_facade = FakeUsersFacade([])
    handler = AddMemberCommandHandler(uow, users_facade)

    result = await handler.handle(
        AddMemberCommand(chat_id=chat.id, user_id=owner_id, user_ids=[uuid4()])
    )

    assert result.is_err
    assert isinstance(result.error, TargetUserNotFoundError)


async def test_non_owner_cannot_add_member() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    owner_id, other_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=other_id, chat_id=chat.id),
        ]
    )
    users_facade = FakeUsersFacade([])
    handler = AddMemberCommandHandler(uow, users_facade)

    result = await handler.handle(
        AddMemberCommand(chat_id=chat.id, user_id=other_id, user_ids=[uuid4()])
    )

    assert result.is_err
    assert isinstance(result.error, NotChatOwnerError)


async def test_cannot_add_member_to_private_chat() -> None:
    chats, members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeChatUnitOfWork(chats, members)
    user_a, user_b = uuid4(), uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    await members.add_members(
        [
            MemberCreate(user_id=user_a, chat_id=chat.id),
            MemberCreate(user_id=user_b, chat_id=chat.id),
        ]
    )
    users_facade = FakeUsersFacade([])
    handler = AddMemberCommandHandler(uow, users_facade)

    result = await handler.handle(
        AddMemberCommand(chat_id=chat.id, user_id=user_a, user_ids=[uuid4()])
    )

    assert result.is_err
    assert isinstance(result.error, CannotModifyPrivateChatError)
