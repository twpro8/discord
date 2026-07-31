from uuid import uuid4

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.messages.application.queries.list_channel_messages import (
    ListChannelMessagesQuery,
    ListChannelMessagesQueryHandler,
)
from src.modules.messages.domain.entities.dtos import MessageCreate
from src.modules.messages.domain.exceptions import ChannelNotFoundError
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
    handler = ListChannelMessagesQueryHandler(uow, servers_facade)

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

    result = await handler.handle(
        ListChannelMessagesQuery(channel_id=channel.id, user_id=user_id, limit=20)
    )

    assert result.is_ok
    assert [m.sequence for m in result.value.items] == [1, 2, 3]


async def test_rejects_unknown_channel() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    handler = ListChannelMessagesQueryHandler(uow, servers_facade)

    result = await handler.handle(
        ListChannelMessagesQuery(channel_id=uuid4(), user_id=uuid4(), limit=20)
    )

    assert result.is_err
    assert isinstance(result.error, ChannelNotFoundError)


async def test_rejects_non_server_member() -> None:
    channels = FakeChannelRepository()
    uow = FakeMessageUnitOfWork(FakeMessageRepository(), FakeChatRepository(), channels)
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    handler = ListChannelMessagesQueryHandler(uow, servers_facade)

    channel = await channels.create(
        ChannelCreate(server_id=uuid4(), name="general", topic=None)
    )

    result = await handler.handle(
        ListChannelMessagesQuery(channel_id=channel.id, user_id=uuid4(), limit=20)
    )

    assert result.is_err
    assert isinstance(result.error, NotServerMemberError)
