from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.kernel.dependencies import SessionDep
from src.modules.channel.repository import ChannelRepository
from src.modules.channel.service import ChannelService
from src.modules.channel.unit_of_work import ChannelUnitOfWork


def get_channel_repository(
    session: SessionDep,
) -> ChannelRepository:
    return ChannelRepository(session=session)


def get_channel_service(
    session: SessionDep,
    channel_unit_of_work: ChannelUnitOfWorkDep,
) -> ChannelService:
    return ChannelService(
        session=session,
        channel_unit_of_work=channel_unit_of_work,
    )


async def get_channel_unit_of_work(
    session: SessionDep,
    channel_repository: ChannelRepositoryDep,
) -> AsyncGenerator[ChannelUnitOfWork]:
    async with ChannelUnitOfWork(session, channel_repository) as channel_unit_of_work:
        yield channel_unit_of_work


ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
ChannelServiceDep = Annotated[ChannelService, Depends(get_channel_service)]
ChannelUnitOfWorkDep = Annotated[ChannelUnitOfWork, Depends(get_channel_unit_of_work)]
