from uuid import UUID, uuid4

import pytest

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.usecases.get_channels import GetChannelsUseCase
from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import NotServerMemberError
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def _make_member_channel(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
    user_id: UUID,
    name: str = "general",
) -> tuple[Channel, UUID]:
    server = await servers.create(ServerCreate(name="Server", owner_id=user_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
    )
    channel = await channels.create(
        ChannelCreate(server_id=server.id, name=name, topic=None)
    )
    return channel, server.id


def _use_case(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
) -> GetChannelsUseCase:
    servers_facade = FakeServersFacade(server_members, servers)
    return GetChannelsUseCase(channels, servers_facade)


async def test_returns_channels_for_server() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id = uuid4()
    _, server_id = await _make_member_channel(
        channels, server_members, servers, user_id
    )
    await channels.create(ChannelCreate(server_id=server_id, name="second", topic=None))

    result = await use_case(user_id=user_id, server_id=server_id)

    assert len(result) == 2
    names = {ch.name for ch in result}
    assert names == {"general", "second"}


async def test_returns_empty_list_for_server_without_channels() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id = uuid4()
    server = await servers.create(ServerCreate(name="Server", owner_id=user_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=server.id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
    )

    result = await use_case(user_id=user_id, server_id=server.id)

    assert result == []


async def test_does_not_return_other_servers_channels() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id = uuid4()
    _, server_id = await _make_member_channel(
        channels, server_members, servers, user_id
    )
    other_server = await servers.create(ServerCreate(name="Other", owner_id=user_id))
    await channels.create(
        ChannelCreate(server_id=other_server.id, name="other", topic=None)
    )

    result = await use_case(user_id=user_id, server_id=server_id)

    assert len(result) == 1
    assert result[0].name == "general"


async def test_non_member_cannot_list() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id, outsider_id = uuid4(), uuid4()
    _, server_id = await _make_member_channel(
        channels, server_members, servers, user_id
    )

    with pytest.raises(NotServerMemberError):
        await use_case(user_id=outsider_id, server_id=server_id)
