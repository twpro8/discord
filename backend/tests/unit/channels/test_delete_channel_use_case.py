from uuid import UUID, uuid4

import pytest

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.exceptions import (
    ChannelNotFoundError,
    OnlyChannelDeletionError,
)
from src.modules.channels.usecases.delete_channel import DeleteChannelUseCase
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


async def _make_owned_server(
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
    owner_id: UUID,
) -> UUID:
    server = await servers.create(ServerCreate(name="Server", owner_id=owner_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=owner_id,
            role=ServerMemberRole.owner,
        )
    )
    return server.id


def _use_case(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
) -> tuple[DeleteChannelUseCase, FakeChannelUnitOfWork]:
    uow = FakeChannelUnitOfWork(channels)
    servers_facade = FakeServersFacade(server_members, servers)
    return DeleteChannelUseCase(uow, servers_facade), uow


async def test_owner_can_delete_extra_channel_and_commit() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, uow = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await channels.create(ChannelCreate(server_id=server_id, name="extra", topic=None))

    await use_case(channel_id=channel.id, user_id=owner_id, server_id=server_id)

    assert await channels.find_by_id(channel.id) is None
    assert uow.committed


async def test_deleting_only_channel_is_rejected() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, uow = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )

    with pytest.raises(OnlyChannelDeletionError):
        await use_case(channel_id=channel.id, user_id=owner_id, server_id=server_id)

    assert await channels.find_by_id(channel.id) is not None
    assert not uow.committed


async def test_channel_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, uow = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)

    with pytest.raises(ChannelNotFoundError):
        await use_case(channel_id=uuid4(), user_id=owner_id, server_id=server_id)

    assert not uow.committed


async def test_server_mismatch_is_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, _ = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await channels.create(ChannelCreate(server_id=server_id, name="extra", topic=None))

    with pytest.raises(ChannelNotFoundError):
        await use_case(channel_id=channel.id, user_id=owner_id, server_id=uuid4())

    assert await channels.find_by_id(channel.id) is not None


async def test_non_owner_member_cannot_delete() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, _ = _use_case(channels, server_members, servers)
    owner_id, member_id = uuid4(), uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=member_id)
    )
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await channels.create(ChannelCreate(server_id=server_id, name="extra", topic=None))

    with pytest.raises(NotServerOwnerError):
        await use_case(channel_id=channel.id, user_id=member_id, server_id=server_id)

    assert await channels.find_by_id(channel.id) is not None


async def test_non_member_cannot_delete() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case, _ = _use_case(channels, server_members, servers)
    owner_id, outsider_id = uuid4(), uuid4()
    server_id = await _make_owned_server(server_members, servers, owner_id)
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await channels.create(ChannelCreate(server_id=server_id, name="extra", topic=None))

    with pytest.raises(NotServerMemberError):
        await use_case(channel_id=channel.id, user_id=outsider_id, server_id=server_id)

    assert await channels.find_by_id(channel.id) is not None
