from uuid import uuid4

from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
    CreateChannelCommandHandler,
)
from src.modules.channels.domain.enums import ChannelType
from tests.unit.channels.fakes import FakeChannelRepository, FakeChannelUnitOfWork


def _handler() -> tuple[CreateChannelCommandHandler, FakeChannelUnitOfWork]:
    uow = FakeChannelUnitOfWork(FakeChannelRepository())
    return CreateChannelCommandHandler(uow), uow


async def test_creates_channel_and_commits_by_default() -> None:
    handler, uow = _handler()
    server_id = uuid4()

    result = await handler.handle(
        CreateChannelCommand(server_id=server_id, name="general")
    )

    assert result.is_ok
    channel = result.value
    assert channel.server_id == server_id
    assert channel.name == "general"
    assert channel.type == ChannelType.text
    assert channel.is_private is False
    assert uow.committed


async def test_is_commit_false_skips_commit() -> None:
    handler, uow = _handler()

    result = await handler.handle(
        CreateChannelCommand(server_id=uuid4(), name="general", is_commit=False)
    )

    assert result.is_ok
    assert not uow.committed
