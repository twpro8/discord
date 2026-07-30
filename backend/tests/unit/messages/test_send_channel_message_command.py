from uuid import uuid4

from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
    SendChannelMessageCommandHandler,
)
from src.modules.messages.domain.entities.dtos import MessageCreateData
from src.modules.messages.domain.exceptions import ChannelNotFoundError
from src.modules.servers.domain.entities.server_member import ServerMemberCreate
from src.modules.servers.domain.exceptions import NotServerMemberError
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import FakeChatRepository
from tests.unit.messages.fakes import FakeMessageRepository, FakeMessageUnitOfWork
from tests.unit.servers.fakes import FakeServerMemberRepository, FakeServersFacade


def _handler() -> tuple[
    SendChannelMessageCommandHandler, FakeChannelRepository, FakeServerMemberRepository
]:
    channels = FakeChannelRepository()
    server_members = FakeServerMemberRepository()
    uow = FakeMessageUnitOfWork(
        FakeMessageRepository(),
        FakeChatRepository(),
        channels,
    )
    servers_facade = FakeServersFacade(server_members)
    return (
        SendChannelMessageCommandHandler(uow, servers_facade),
        channels,
        server_members,
    )


async def test_rejects_unknown_channel() -> None:
    handler, _, _ = _handler()

    result = await handler.handle(
        SendChannelMessageCommand(
            channel_id=uuid4(),
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ChannelNotFoundError)


async def test_rejects_non_server_member() -> None:
    handler, channels, _ = _handler()
    channel = await channels.create(
        ChannelCreate(server_id=uuid4(), name="general", topic=None)
    )

    result = await handler.handle(
        SendChannelMessageCommand(
            channel_id=channel.id,
            sender_id=uuid4(),
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotServerMemberError)


async def test_success() -> None:
    handler, channels, server_members = _handler()
    server_id = uuid4()
    sender_id = uuid4()
    channel = await channels.create(
        ChannelCreate(server_id=server_id, name="general", topic=None)
    )
    await server_members.create(
        ServerMemberCreate(server_id=server_id, user_id=sender_id)
    )

    result = await handler.handle(
        SendChannelMessageCommand(
            channel_id=channel.id,
            sender_id=sender_id,
            data=MessageCreateData(body="hello"),
        )
    )

    assert result.is_ok
    message = result.value
    assert message.body == "hello"
    assert message.channel_id == channel.id
    assert message.sequence == 1
