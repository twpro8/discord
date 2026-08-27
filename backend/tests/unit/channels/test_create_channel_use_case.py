from uuid import uuid4

from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.usecases.create_channel import CreateChannelUseCase
from tests.unit.channels.fakes import FakeChannelRepository, FakeChannelUnitOfWork


def _use_case() -> tuple[CreateChannelUseCase, FakeChannelUnitOfWork]:
    uow = FakeChannelUnitOfWork(FakeChannelRepository())
    return CreateChannelUseCase(uow), uow


async def test_creates_channel_and_commits_by_default() -> None:
    use_case, uow = _use_case()
    server_id = uuid4()

    channel = await use_case(server_id=server_id, name="general")

    assert channel.server_id == server_id
    assert channel.name == "general"
    assert channel.type == ChannelType.text
    assert channel.is_private is False
    assert uow.committed


async def test_is_commit_false_skips_commit() -> None:
    use_case, uow = _use_case()

    await use_case(server_id=uuid4(), name="general", is_commit=False)

    assert not uow.committed
