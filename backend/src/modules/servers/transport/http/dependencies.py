from collections.abc import AsyncGenerator
from contextlib import aclosing
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import RoomMembershipUpdaterDep, SessionDep
from src.modules.channels.public.facade import ChannelsFacade, build_channels_facade
from src.modules.servers.adapters.persistence.server_invite_repository_impl import (
    ServerInviteRepositoryImpl,
)
from src.modules.servers.adapters.persistence.server_member_repository_impl import (
    ServerMemberRepositoryImpl,
)
from src.modules.servers.adapters.persistence.server_repository_impl import (
    ServerRepositoryImpl,
)
from src.modules.servers.adapters.server_unit_of_work_impl import (
    ServerUnitOfWorkImpl,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.modules.servers.usecases.create_invite import CreateInviteUseCase
from src.modules.servers.usecases.create_server import CreateServerUseCase
from src.modules.servers.usecases.delete_invite import DeleteInviteUseCase
from src.modules.servers.usecases.delete_server import DeleteServerUseCase
from src.modules.servers.usecases.get_invites import GetInvitesUseCase
from src.modules.servers.usecases.get_server_members import GetServerMembersUseCase
from src.modules.servers.usecases.get_server_where_user_member import (
    GetServerWhereUserMemberUseCase,
)
from src.modules.servers.usecases.get_servers_where_user_member import (
    GetServersWhereUserMemberUseCase,
)
from src.modules.servers.usecases.join_server import JoinServerUseCase
from src.modules.servers.usecases.transfer_ownership import (
    TransferServerOwnershipUseCase,
)
from src.modules.servers.usecases.update_server import UpdateServerUseCase


async def get_server_unit_of_work(
    session: SessionDep,
) -> AsyncGenerator[ServerUnitOfWork]:
    server_repository = ServerRepositoryImpl(session=session)
    server_member_repository = ServerMemberRepositoryImpl(session=session)
    server_invite_repository = ServerInviteRepositoryImpl(session=session)
    async with ServerUnitOfWorkImpl(
        session,
        server_repository,
        server_member_repository,
        server_invite_repository,
    ) as uow:
        yield uow


async def get_channels_facade(session: SessionDep) -> AsyncGenerator[ChannelsFacade]:
    # CreateServerUseCase delegates default-channel creation to channels as
    # part of its own atomic operation, so it needs a same-session facade.
    async with aclosing(build_channels_facade(session)) as facades:
        async for facade in facades:
            yield facade


ServerUnitOfWorkDep = Annotated[ServerUnitOfWork, Depends(get_server_unit_of_work)]
ChannelsFacadeDep = Annotated[ChannelsFacade, Depends(get_channels_facade)]


async def get_create_server_use_case(
    uow: ServerUnitOfWorkDep,
    channels_facade: ChannelsFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> CreateServerUseCase:
    return CreateServerUseCase(uow, channels_facade, room_membership_updater)


async def get_update_server_use_case(
    uow: ServerUnitOfWorkDep,
) -> UpdateServerUseCase:
    return UpdateServerUseCase(uow)


async def get_delete_server_use_case(
    uow: ServerUnitOfWorkDep,
) -> DeleteServerUseCase:
    return DeleteServerUseCase(uow)


async def get_transfer_server_ownership_use_case(
    uow: ServerUnitOfWorkDep,
) -> TransferServerOwnershipUseCase:
    return TransferServerOwnershipUseCase(uow)


async def get_join_server_use_case(
    uow: ServerUnitOfWorkDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> JoinServerUseCase:
    return JoinServerUseCase(uow, room_membership_updater)


async def get_create_invite_use_case(
    uow: ServerUnitOfWorkDep,
) -> CreateInviteUseCase:
    return CreateInviteUseCase(uow)


async def get_delete_invite_use_case(
    uow: ServerUnitOfWorkDep,
) -> DeleteInviteUseCase:
    return DeleteInviteUseCase(uow)


async def get_get_invites_use_case(
    uow: ServerUnitOfWorkDep,
) -> GetInvitesUseCase:
    return GetInvitesUseCase(uow.servers, uow.invites)


async def get_get_server_members_use_case(
    uow: ServerUnitOfWorkDep,
) -> GetServerMembersUseCase:
    return GetServerMembersUseCase(uow.server_members)


async def get_get_server_where_user_member_use_case(
    uow: ServerUnitOfWorkDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> GetServerWhereUserMemberUseCase:
    return GetServerWhereUserMemberUseCase(uow.servers, room_membership_updater)


async def get_get_servers_where_user_member_use_case(
    uow: ServerUnitOfWorkDep,
) -> GetServersWhereUserMemberUseCase:
    return GetServersWhereUserMemberUseCase(uow.servers)


CreateServerUseCaseDep = Annotated[
    CreateServerUseCase, Depends(get_create_server_use_case)
]
UpdateServerUseCaseDep = Annotated[
    UpdateServerUseCase, Depends(get_update_server_use_case)
]
DeleteServerUseCaseDep = Annotated[
    DeleteServerUseCase, Depends(get_delete_server_use_case)
]
TransferServerOwnershipUseCaseDep = Annotated[
    TransferServerOwnershipUseCase, Depends(get_transfer_server_ownership_use_case)
]
JoinServerUseCaseDep = Annotated[JoinServerUseCase, Depends(get_join_server_use_case)]
CreateInviteUseCaseDep = Annotated[
    CreateInviteUseCase, Depends(get_create_invite_use_case)
]
DeleteInviteUseCaseDep = Annotated[
    DeleteInviteUseCase, Depends(get_delete_invite_use_case)
]
GetInvitesUseCaseDep = Annotated[GetInvitesUseCase, Depends(get_get_invites_use_case)]
GetServerMembersUseCaseDep = Annotated[
    GetServerMembersUseCase, Depends(get_get_server_members_use_case)
]
GetServerWhereUserMemberUseCaseDep = Annotated[
    GetServerWhereUserMemberUseCase, Depends(get_get_server_where_user_member_use_case)
]
GetServersWhereUserMemberUseCaseDep = Annotated[
    GetServersWhereUserMemberUseCase,
    Depends(get_get_servers_where_user_member_use_case),
]
