from uuid import uuid4

from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.usecases.create_channel import CreateChannelUseCase
from tests.unit.channels.fakes import FakeChannelRepository


async def test_creates_channel() -> None:
    use_case = CreateChannelUseCase(FakeChannelRepository())
    server_id = uuid4()

    channel = await use_case(server_id=server_id, name="general")

    assert channel.server_id == server_id
    assert channel.name == "general"
    assert channel.type == ChannelType.text
    assert channel.is_private is False
