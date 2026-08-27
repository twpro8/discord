from uuid import uuid4

import pytest

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.messages.domain.entities.dtos import MessageCreate
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.usecases.list_channel_messages import (
    ListChannelMessagesUseCase,
)
from src.modules.servers.domain.entities.dtos import ServerMemberCreate
from src.modules.servers.domain.exceptions import NotServerMemberError
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import FakeChatRepository
from tests.unit.messages.fakes import FakeMessageRepository, FakeMessageUnitOfWork
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def test_returns_messages_in_ascending_order() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    server_members = FakeServerMemberRepository()
    servers_facade = FakeServersFacade(server_members, FakeServerRepository())
    use_case = ListChannelMessagesUseCase(uow, servers_facade)

    user_id, server_id = uuid4(), uuid4()
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=user_id)
    )
    for seq in (1, 2, 3):
        await uow.messages.create(
            MessageCreate(
                sender_id=user_id,
                body=f"msg{seq}",
                sequence=seq,
                parent_id=None,
                channel_id=channel.id,
            )
        )

    page = await use_case(channel_id=channel.id, user_id=user_id, limit=20)

    assert [m.sequence for m in page.items] == [1, 2, 3]


async def test_rejects_unknown_channel() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    use_case = ListChannelMessagesUseCase(uow, servers_facade)

    with pytest.raises(ChannelNotFoundError):
        await use_case(channel_id=uuid4(), user_id=uuid4(), limit=20)


async def test_rejects_non_server_member() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    use_case = ListChannelMessagesUseCase(uow, servers_facade)

    channel = await channels.create(
        ChannelCreate(server_id=uuid4(), name="general", topic=None)
    )

    with pytest.raises(NotServerMemberError):
        await use_case(channel_id=channel.id, user_id=uuid4(), limit=20)
