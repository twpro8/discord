from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.schemas import ChannelCreate
from src.modules.channels.domain.enums import ChannelType
from src.modules.channels.infrastructure.unit_of_work import ChannelUnitOfWork
from src.shared.services.base_service import BaseService


class ChannelService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        channel_unit_of_work: ChannelUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = channel_unit_of_work

    async def create_channel(
        self,
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

        channel = await self.uow.channels.create(channel_data)
        if is_commit:
            await self.uow.commit()

        return channel
