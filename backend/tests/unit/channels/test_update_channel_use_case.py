from uuid import UUID, uuid4

import pytest

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import (
    ChannelCreate,
    ChannelUpdate,
    ChannelUpdateData,
)
from src.modules.channels.domain.exceptions import (
    ChannelConflictError,
    ChannelNotFoundError,
)
from src.modules.channels.usecases.update_channel import UpdateChannelUseCase
from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    NotServerMemberError,
    NotServerOwnerError,
)
from tests.unit.channels.fakes import FakeChannelRepository
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


def _use_case(
    channels: FakeChannelRepository,
    server_members: FakeServerMemberRepository,
    servers: FakeServerRepository,
) -> UpdateChannelUseCase:
    servers_facade = FakeServersFacade(server_members, servers)
    return UpdateChannelUseCase(channels, servers_facade)


async def test_owner_can_rename_channel() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    updated = await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(name="renamed", topic="new topic"),
    )

    assert updated.name == "renamed"
    assert updated.topic == "new topic"


async def test_partial_update_leaves_other_fields_untouched() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )

    updated = await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(topic="only topic"),
    )

    assert updated.name == "general"
    assert updated.topic == "only topic"


async def test_empty_topic_clears_field() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )
    await channels.update(channel.id, ChannelUpdate(topic="some topic"))

    updated = await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(topic=""),
    )

    assert updated.topic is None


async def test_position_updated() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    updated = await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(position=5),
    )

    assert updated.position == 5


async def test_renaming_to_same_name_is_allowed() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(name="general"),
    )


async def test_duplicate_name_within_server_conflicts() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )
    await channels.create(ChannelCreate(server_id=server_id, name="taken"))

    with pytest.raises(ChannelConflictError):
        await use_case(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="taken"),
        )


async def test_same_name_in_another_server_does_not_conflict() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id, name="general"
    )
    other_server_id = uuid4()
    await channels.create(ChannelCreate(server_id=other_server_id, name="renamed"))

    updated = await use_case(
        channel_id=channel.id,
        user_id=owner_id,
        server_id=server_id,
        update_data=ChannelUpdateData(name="renamed"),
    )

    assert updated.name == "renamed"


async def test_channel_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    _, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    with pytest.raises(ChannelNotFoundError):
        await use_case(
            channel_id=uuid4(),
            user_id=owner_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )


async def test_server_mismatch_is_not_found() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id = uuid4()
    channel, _ = await _make_owned_channel(channels, server_members, servers, owner_id)

    with pytest.raises(ChannelNotFoundError):
        await use_case(
            channel_id=channel.id,
            user_id=owner_id,
            server_id=uuid4(),
            update_data=ChannelUpdateData(name="renamed"),
        )


async def test_non_owner_member_cannot_update() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id, member_id = uuid4(), uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=member_id)
    )

    with pytest.raises(NotServerOwnerError):
        await use_case(
            channel_id=channel.id,
            user_id=member_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )


async def test_non_member_cannot_update() -> None:
    channels, server_members, servers = (
        FakeChannelRepository(),
        FakeServerMemberRepository(),
        FakeServerRepository(),
    )
    use_case = _use_case(channels, server_members, servers)
    owner_id, outsider_id = uuid4(), uuid4()
    channel, server_id = await _make_owned_channel(
        channels, server_members, servers, owner_id
    )

    with pytest.raises(NotServerMemberError):
        await use_case(
            channel_id=channel.id,
            user_id=outsider_id,
            server_id=server_id,
            update_data=ChannelUpdateData(name="renamed"),
        )
