from uuid import uuid4

import pytest

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.messages.domain.entities.dtos import MessageCreateData
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.messages.usecases.send_channel_message import (
    SendChannelMessageUseCase,
)
from src.modules.servers.domain.entities.dtos import ServerMemberCreate
from src.modules.servers.domain.exceptions import NotServerMemberError
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.messages.fakes import FakeMessageRepository
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


def _use_case() -> tuple[
    SendChannelMessageUseCase, FakeChannelRepository, FakeServerMemberRepository
]:
    channels = FakeChannelRepository()
    server_members = FakeServerMemberRepository()
    servers_facade = FakeServersFacade(server_members, FakeServerRepository())
    return (
        SendChannelMessageUseCase(FakeMessageRepository(), channels, servers_facade),
        channels,
        server_members,
    )


async def test_rejects_unknown_channel() -> None:
    use_case, _, _ = _use_case()

    with pytest.raises(ChannelNotFoundError):
        await use_case(
            channel_id=uuid4(),
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )


async def test_rejects_non_server_member() -> None:
    use_case, channels, _ = _use_case()
    channel = await channels.create(
        ChannelCreate(server_id=uuid4(), name="general", topic=None)
    )

    with pytest.raises(NotServerMemberError):
        await use_case(
            channel_id=channel.id,
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )


async def test_success() -> None:
    use_case, channels, server_members = _use_case()
    server_id = uuid4()
    sender_id = uuid4()
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=sender_id)
    )

    message = await use_case(
        channel_id=channel.id,
        sender_id=sender_id,
        data=MessageCreateData(body="hello"),
    )

    assert message.body == "hello"
    assert message.channel_id == channel.id
    assert message.sequence == 1
