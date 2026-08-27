from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelCreate
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)


class CreateChannelUseCase:
    def __init__(self, channel_unit_of_work: ChannelUnitOfWork) -> None:
        self._uow = channel_unit_of_work

    async def __call__(
        self,
        *,
        server_id: UUID,
        name: str,
        type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
        is_commit: bool = True,
    ) -> Channel:
        channel_data = ChannelCreate(
            server_id=server_id,
            name=name,
            type=type,
            position=0,
            topic=topic,
            is_private=is_private,
        )

        channel = await self._uow.channels.create(channel_data)
        if is_commit:
            await self._uow.commit()

        return channel
