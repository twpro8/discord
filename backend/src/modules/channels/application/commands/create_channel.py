from uuid import UUID

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    AbstractChannelUnitOfWork,
)
from src.modules.channels.transport.http.schemas import ChannelCreateSchema


class CreateChannelCommand:
    def __init__(self, uow: AbstractChannelUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self,
        server_id: UUID,
        name: str,
        type: ChannelType = ChannelType.text,
        topic: str | None = None,
        is_private: bool = False,
    ) -> Channel:
        channel_data = ChannelCreateSchema(
            server_id=server_id,
            name=name,
            type=type,
            position=0,
            topic=topic,
            is_private=is_private,
        )
        channel = await self._uow.channels.create(channel_data)
        await self._uow.commit()
        return channel
