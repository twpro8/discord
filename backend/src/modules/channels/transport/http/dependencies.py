from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep, TransactionDep
from src.modules.channels.adapters.persistence.channel_repository_impl import (
    ChannelRepositoryImpl,
)
from src.modules.channels.domain.repositories.channel_repository import (
    ChannelRepository,
)
from src.modules.channels.usecases.create_channel import CreateChannelUseCase
from src.modules.channels.usecases.delete_channel import DeleteChannelUseCase
from src.modules.channels.usecases.update_channel import UpdateChannelUseCase
from src.modules.servers.public.facade import ServersFacade, build_servers_facade


def get_channel_repository(session: SessionDep) -> ChannelRepository:
    return ChannelRepositoryImpl(session)


def get_servers_facade(session: SessionDep) -> ServersFacade:
    return build_servers_facade(session)


ChannelRepositoryDep = Annotated[ChannelRepository, Depends(get_channel_repository)]
ServersFacadeDep = Annotated[ServersFacade, Depends(get_servers_facade)]


async def get_create_channel_use_case(
    channel_repository: ChannelRepositoryDep,
    _tx: TransactionDep,
) -> CreateChannelUseCase:
    # CreateChannelUseCase never commits itself (see its docstring) — this
    # unused _tx forces the request's auto-commit dependency to actually
    # build, since nothing else in this provider's graph references it.
    return CreateChannelUseCase(channel_repository)


async def get_update_channel_use_case(
    channel_repository: ChannelRepositoryDep,
    servers_facade: ServersFacadeDep,
    _tx: TransactionDep,
) -> UpdateChannelUseCase:
    return UpdateChannelUseCase(channel_repository, servers_facade)


async def get_delete_channel_use_case(
    channel_repository: ChannelRepositoryDep,
    servers_facade: ServersFacadeDep,
    _tx: TransactionDep,
) -> DeleteChannelUseCase:
    return DeleteChannelUseCase(channel_repository, servers_facade)


CreateChannelUseCaseDep = Annotated[
    CreateChannelUseCase, Depends(get_create_channel_use_case)
]
UpdateChannelUseCaseDep = Annotated[
    UpdateChannelUseCase, Depends(get_update_channel_use_case)
]
DeleteChannelUseCaseDep = Annotated[
    DeleteChannelUseCase, Depends(get_delete_channel_use_case)
]
