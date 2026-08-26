from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.domain.repositories.channel_unit_of_work import (
    ChannelUnitOfWork,
)
from src.modules.channels.infrastructure.channel_unit_of_work_impl import (
    ChannelUnitOfWorkImpl,
)
from src.modules.channels.infrastructure.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.channels.usecases.create_channel import CreateChannelUseCase
from src.modules.channels.usecases.delete_channel import DeleteChannelUseCase
from src.modules.channels.usecases.update_channel import UpdateChannelUseCase
from src.modules.servers.public.facade import ServersFacade, build_servers_facade


async def get_channel_unit_of_work(
    session: SessionDep,
) -> AsyncGenerator[ChannelUnitOfWork]:
    channel_repository = ChannelRepositoryImpl(session)
    async with ChannelUnitOfWorkImpl(
        session=session, channel_repository=channel_repository
    ) as uow:
        yield uow


async def get_servers_facade(session: SessionDep) -> ServersFacade:
    return build_servers_facade(session)


ChannelUnitOfWorkDep = Annotated[ChannelUnitOfWork, Depends(get_channel_unit_of_work)]
ServersFacadeDep = Annotated[ServersFacade, Depends(get_servers_facade)]


async def get_create_channel_use_case(
    uow: ChannelUnitOfWorkDep,
) -> CreateChannelUseCase:
    return CreateChannelUseCase(uow)


async def get_update_channel_use_case(
    uow: ChannelUnitOfWorkDep, servers_facade: ServersFacadeDep
) -> UpdateChannelUseCase:
    return UpdateChannelUseCase(uow, servers_facade)


async def get_delete_channel_use_case(
    uow: ChannelUnitOfWorkDep, servers_facade: ServersFacadeDep
) -> DeleteChannelUseCase:
    return DeleteChannelUseCase(uow, servers_facade)


CreateChannelUseCaseDep = Annotated[
    CreateChannelUseCase, Depends(get_create_channel_use_case)
]
UpdateChannelUseCaseDep = Annotated[
    UpdateChannelUseCase, Depends(get_update_channel_use_case)
]
DeleteChannelUseCaseDep = Annotated[
    DeleteChannelUseCase, Depends(get_delete_channel_use_case)
]
