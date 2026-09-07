from uuid import UUID, uuid4

import pytest

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.exceptions import ChannelNotFoundError
from src.modules.channels.usecases.get_channel_by_id import GetChannelByIDUseCase
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
) -> GetChannelByIDUseCase:
    servers_facade = FakeServersFacade(server_members, servers)
    return GetChannelByIDUseCase(channels, servers_facade)


async def test_returns_channel() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id = uuid4()
    channel, server_id = await _make_member_channel(
        channels, server_members, servers, user_id
    )

    result = await use_case(user_id=user_id, channel_id=channel.id, server_id=server_id)

    assert result.id == channel.id
    assert result.name == "general"
    assert result.server_id == server_id


async def test_channel_not_found() -> None:
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

    with pytest.raises(ChannelNotFoundError):
        await use_case(user_id=user_id, channel_id=uuid4(), server_id=server_id)


async def test_server_mismatch_is_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id = uuid4()
    channel, _ = await _make_member_channel(channels, server_members, servers, user_id)
    other_server = await servers.create(ServerCreate(name="Other", owner_id=user_id))
    await server_members.create(
        ServerMemberCreate(
            server_id=other_server.id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
    )

    with pytest.raises(ChannelNotFoundError):
        await use_case(
            user_id=user_id, channel_id=channel.id, server_id=other_server.id
        )


async def test_non_member_cannot_get() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    user_id, outsider_id = uuid4(), uuid4()
    channel, server_id = await _make_member_channel(
        channels, server_members, servers, user_id
    )

    with pytest.raises(NotServerMemberError):
        await use_case(user_id=outsider_id, channel_id=channel.id, server_id=server_id)


async def test_owner_can_get() -> None:
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
            role=ServerMemberRole.owner,
        )
    )
    channel = await channels.create(
        ChannelCreate(server_id=server.id, name="general", topic=None)
    )

    result = await use_case(user_id=user_id, channel_id=channel.id, server_id=server.id)

    assert result.id == channel.id
