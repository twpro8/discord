from uuid import uuid4

import pytest

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.chats.domain.entities.dtos import ChatCreate, MemberCreate
from src.modules.chats.domain.enums import ChatMemberRole, ChatType
from src.modules.messages.domain.entities.dtos import MessageCreate
from src.modules.messages.domain.exceptions import MessageDeletePermissionError
from src.modules.messages.usecases.delete_message import DeleteMessageUseCase
from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import (
    FakeChatMemberRepository,
    FakeChatRepository,
    FakeChatsFacade,
)
from tests.unit.messages.fakes import FakeMessageRepository, FakeMessageUnitOfWork
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def test_sender_can_delete_own_chat_message() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), chats, FakeChannelRepository())
    chats_facade = FakeChatsFacade(chats, chat_members)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    use_case = DeleteMessageUseCase(uow, chats_facade, servers_facade)

    sender_id = uuid4()
    chat = await chats.create(ChatCreate(type=ChatType.private))
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id, body="hi", sequence=1, parent_id=None, chat_id=chat.id
        )
    )

    deleted = await use_case(message_id=message.id, user_id=sender_id)

    assert deleted.is_deleted is True
    assert deleted.body is None
    assert uow.committed


async def test_chat_owner_can_delete_others_message() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), chats, FakeChannelRepository())
    chats_facade = FakeChatsFacade(chats, chat_members)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    use_case = DeleteMessageUseCase(uow, chats_facade, servers_facade)

    owner_id, sender_id = uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await chat_members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=sender_id, chat_id=chat.id),
        ]
    )
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id, body="hi", sequence=1, parent_id=None, chat_id=chat.id
        )
    )

    deleted = await use_case(message_id=message.id, user_id=owner_id)

    assert deleted.is_deleted is True


async def test_non_sender_non_owner_cannot_delete_chat_message() -> None:
    chats, chat_members = FakeChatRepository(), FakeChatMemberRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), chats, FakeChannelRepository())
    chats_facade = FakeChatsFacade(chats, chat_members)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    use_case = DeleteMessageUseCase(uow, chats_facade, servers_facade)

    owner_id, sender_id, other_id = uuid4(), uuid4(), uuid4()
    chat = await chats.create(
        ChatCreate(type=ChatType.group, owner_id=owner_id, name="G")
    )
    await chat_members.add_members(
        [
            MemberCreate(user_id=owner_id, chat_id=chat.id, role=ChatMemberRole.owner),
            MemberCreate(user_id=sender_id, chat_id=chat.id),
            MemberCreate(user_id=other_id, chat_id=chat.id),
        ]
    )
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id, body="hi", sequence=1, parent_id=None, chat_id=chat.id
        )
    )

    with pytest.raises(MessageDeletePermissionError):
        await use_case(message_id=message.id, user_id=other_id)


async def test_server_owner_can_delete_channel_message() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    server_members, servers = FakeServerMemberRepository(), FakeServerRepository()
    chats_facade = FakeChatsFacade(FakeChatRepository(), FakeChatMemberRepository())
    servers_facade = FakeServersFacade(server_members, servers)
    use_case = DeleteMessageUseCase(uow, chats_facade, servers_facade)

    owner_id, sender_id = uuid4(), uuid4()
    await servers.create(ServerCreate(name="S", owner_id=owner_id))
    server = next(iter(servers.servers.values()))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    channel = await channels.create(
        ChannelCreate(server_id=server.id, name="general", topic=None)
    )
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hi",
            sequence=1,
            parent_id=None,
            channel_id=channel.id,
        )
    )

    deleted = await use_case(message_id=message.id, user_id=owner_id)

    assert deleted.is_deleted is True
