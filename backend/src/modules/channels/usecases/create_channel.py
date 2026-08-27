from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)


class CreateChannelUseCase:
    """No explicit commit: called directly (auto-committed by the request's
    TransactionDep) or, via ChannelsFacade.create_default_channel, as part
    of another module's own atomic write (e.g. CreateServerUseCase) — that
    caller's own explicit commit covers this write too, since both share
    the same session."""

    def __init__(self, channel_repository: ChannelRepository) -> None:
        self._channels = channel_repository

    async def __call__(
        self,
        *,
        server_id: UUID,
        name: str,
        type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
    ) -> Channel:
        channel_data = ChannelCreate(
            server_id=server_id,
            name=name,
            type=type,
            position=0,
            topic=topic,
            is_private=is_private,
        )

        return await self._channels.create(channel_data)
