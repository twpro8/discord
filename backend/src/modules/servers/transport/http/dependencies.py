from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import RoomMembershipUpdaterDep, SessionDep, TransactionDep
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
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
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


def get_server_repository(session: SessionDep) -> ServerRepository:
    return ServerRepositoryImpl(session=session)


def get_server_member_repository(session: SessionDep) -> ServerMemberRepository:
    return ServerMemberRepositoryImpl(session=session)


def get_server_invite_repository(session: SessionDep) -> ServerInviteRepository:
    return ServerInviteRepositoryImpl(session=session)


def get_channels_facade(session: SessionDep) -> ChannelsFacade:
    # CreateServerUseCase delegates default-channel creation to channels as
    # part of its own atomic operation, so it needs a same-session facade.
    return build_channels_facade(session)


ServerRepositoryDep = Annotated[ServerRepository, Depends(get_server_repository)]
ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
ServerInviteRepositoryDep = Annotated[
    ServerInviteRepository, Depends(get_server_invite_repository)
]
ChannelsFacadeDep = Annotated[ChannelsFacade, Depends(get_channels_facade)]


async def get_create_server_use_case(
    tx: TransactionDep,
    server_repository: ServerRepositoryDep,
    server_member_repository: ServerMemberRepositoryDep,
    channels_facade: ChannelsFacadeDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> CreateServerUseCase:
    return CreateServerUseCase(
        tx,
        server_repository,
        server_member_repository,
        channels_facade,
        room_membership_updater,
    )


async def get_update_server_use_case(
    server_repository: ServerRepositoryDep,
    _tx: TransactionDep,
) -> UpdateServerUseCase:
    return UpdateServerUseCase(server_repository)


async def get_delete_server_use_case(
    server_repository: ServerRepositoryDep,
    _tx: TransactionDep,
) -> DeleteServerUseCase:
    return DeleteServerUseCase(server_repository)


async def get_transfer_server_ownership_use_case(
    server_repository: ServerRepositoryDep,
    server_member_repository: ServerMemberRepositoryDep,
    _tx: TransactionDep,
) -> TransferServerOwnershipUseCase:
    return TransferServerOwnershipUseCase(server_repository, server_member_repository)


async def get_join_server_use_case(
    tx: TransactionDep,
    server_repository: ServerRepositoryDep,
    server_member_repository: ServerMemberRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> JoinServerUseCase:
    return JoinServerUseCase(
        tx,
        server_repository,
        server_member_repository,
        server_invite_repository,
        room_membership_updater,
    )


async def get_create_invite_use_case(
    server_repository: ServerRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
    _tx: TransactionDep,
) -> CreateInviteUseCase:
    return CreateInviteUseCase(server_repository, server_invite_repository)


async def get_delete_invite_use_case(
    server_repository: ServerRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
    _tx: TransactionDep,
) -> DeleteInviteUseCase:
    return DeleteInviteUseCase(server_repository, server_invite_repository)


async def get_get_invites_use_case(
    server_repository: ServerRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
) -> GetInvitesUseCase:
    return GetInvitesUseCase(server_repository, server_invite_repository)


async def get_get_server_members_use_case(
    server_member_repository: ServerMemberRepositoryDep,
) -> GetServerMembersUseCase:
    return GetServerMembersUseCase(server_member_repository)


async def get_get_server_where_user_member_use_case(
    server_repository: ServerRepositoryDep,
    room_membership_updater: RoomMembershipUpdaterDep,
) -> GetServerWhereUserMemberUseCase:
    return GetServerWhereUserMemberUseCase(server_repository, room_membership_updater)


async def get_get_servers_where_user_member_use_case(
    server_repository: ServerRepositoryDep,
) -> GetServersWhereUserMemberUseCase:
    return GetServersWhereUserMemberUseCase(server_repository)


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
