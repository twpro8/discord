from uuid import UUID, uuid4

from src.modules.channels.application.commands.update_channel import (
    UpdateChannelCommand,
    UpdateChannelCommandHandler,
)
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate, ChannelUpdateData
from src.modules.channels.domain.exceptions import (
    ChannelConflictError,
    ChannelNotFoundError,
)
from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    NotServerMemberError,
    NotServerOwnerError,
)
from tests.unit.channels.fakes import FakeChannelRepository, FakeChannelUnitOfWork
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def _make_owned_channel(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
    owner_id: UUID,
    name: str = "general",
) -> tuple[Channel, UUID]:
    server = await servers.create(ServerCreate(name="Server", owner_id=owner_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=owner_id,
            role=ServerMemberRole.owner,
        )
    )
    channel = await channels.create(
        ChannelCreate(server_id=server.id, name=name, topic=None)
    )
    return channel, server.id


def _handler(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
) -> tuple[UpdateChannelCommandHandler, FakeChannelUnitOfWork]:
    uow = FakeChannelUnitOfWork(channels)
    servers_facade = FakeServersFacade(server_members, servers)
    return UpdateChannelCommandHandler(uow, servers_facade), uow


async def test_owner_can_rename_channel_and_commit() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, uow = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed", topic="new topic"),
        )
    )

    assert result.is_ok
    assert result.value.name == "renamed"
    assert result.value.topic == "new topic"
    assert uow.committed


async def test_partial_update_leaves_other_fields_untouched() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, uow = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(topic="only topic"),
        )
    )

    assert result.is_ok
    assert result.value.name == "general"
    assert result.value.topic == "only topic"


async def test_empty_topic_clears_field() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )
    await channels.update(channel.id, ChannelUpdateData(topic="some topic"))

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(topic=""),
        )
    )

    assert result.is_ok
    assert result.value.topic is None


async def test_position_updated() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(position=5),
        )
    )

    assert result.is_ok
    assert result.value.position == 5


async def test_renaming_to_same_name_is_allowed() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="general"),
        )
    )

    assert result.is_ok


async def test_duplicate_name_within_server_conflicts() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, uow = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )
    await channels.create(ChannelCreate(server_id=server_id, name="taken"))

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="taken"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChannelConflictError)
    assert not uow.committed


async def test_same_name_in_another_server_does_not_conflict() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )
    other_server_id = uuid4()
    await channels.create(ChannelCreate(server_id=other_server_id, name="renamed"))

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )
    )

    assert result.is_ok
    assert result.value.name == "renamed"


async def test_channel_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, uow = _handler(channels, server_members, servers)
    owner_id = uuid4()
    _, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=uuid4(),
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChannelNotFoundError)
    assert not uow.committed


async def test_server_mismatch_is_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id = uuid4()
    channel, _ = await _make_owned_channel(channels, server_members, servers, owner_id)

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=uuid4(),
            update_data=ChannelUpdateData(name="renamed"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChannelNotFoundError)


async def test_non_owner_member_cannot_update() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id, member_id = uuid4(), uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=member_id)
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=member_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotServerOwnerError)


async def test_non_member_cannot_update() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    handler, _ = _handler(channels, server_members, servers)
    owner_id, outsider_id = uuid4(), uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    result = await handler.handle(
        UpdateChannelCommand(
            channel_id=channel.id,
            user_id=outsider_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotServerMemberError)
