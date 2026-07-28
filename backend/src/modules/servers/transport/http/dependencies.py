from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.transport.http.dependencies import CreateChannelCommandDep
from src.modules.servers.application.commands.create_invite import CreateInviteCommand
from src.modules.servers.application.commands.create_server import CreateServerCommand
from src.modules.servers.application.commands.delete_invite import DeleteInviteCommand
from src.modules.servers.application.commands.delete_server import DeleteServerCommand
from src.modules.servers.application.commands.join_server import JoinServerCommand
from src.modules.servers.application.commands.transfer_ownership import (
    TransferServerOwnershipCommand,
)
from src.modules.servers.application.commands.update_server import UpdateServerCommand
from src.modules.servers.application.queries.get_invites import GetInvitesQuery
from src.modules.servers.application.queries.get_server_where_user_member import (
    GetServerWhereUserMemberQuery,
)
from src.modules.servers.application.queries.get_servers_where_user_member import (
    GetServersWhereUserMemberQuery,
)
from src.modules.servers.infrastructure.persistence.repository import (
    ServerInviteRepository,
    ServerMemberRepository,
    ServerRepository,
)
from src.modules.servers.infrastructure.unit_of_work import ServerUnitOfWork


def get_server_repository(
    session: SessionDep,
) -> ServerRepository:
    return ServerRepository(session=session)


def get_server_member_repository(
    session: SessionDep,
) -> ServerMemberRepository:
    return ServerMemberRepository(session=session)


def get_server_invite_repository(
    session: SessionDep,
) -> ServerInviteRepository:
    return ServerInviteRepository(session=session)


async def get_server_unit_of_work(
    session: SessionDep,
    server_repository: ServerRepositoryDep,
    server_member_repository: ServerMemberRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
) -> AsyncGenerator[ServerUnitOfWork]:
    async with ServerUnitOfWork(
        session,
        server_repository,
        server_member_repository,
        server_invite_repository,
    ) as server_unit_of_work:
        yield server_unit_of_work


def get_create_server_command(
    server_unit_of_work: ServerUnitOfWorkDep,
    create_channel_command: CreateChannelCommandDep,
) -> CreateServerCommand:
    return CreateServerCommand(
        uow=server_unit_of_work,
        create_channel_command=create_channel_command,
    )


def get_update_server_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> UpdateServerCommand:
    return UpdateServerCommand(uow=server_unit_of_work)


def get_delete_server_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> DeleteServerCommand:
    return DeleteServerCommand(uow=server_unit_of_work)


def get_transfer_ownership_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> TransferServerOwnershipCommand:
    return TransferServerOwnershipCommand(uow=server_unit_of_work)


def get_join_server_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> JoinServerCommand:
    return JoinServerCommand(uow=server_unit_of_work)


def get_create_invite_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> CreateInviteCommand:
    return CreateInviteCommand(uow=server_unit_of_work)


def get_delete_invite_command(
    server_unit_of_work: ServerUnitOfWorkDep,
) -> DeleteInviteCommand:
    return DeleteInviteCommand(uow=server_unit_of_work)


def get_servers_where_user_member_query(
    server_repository: ServerRepositoryDep,
) -> GetServersWhereUserMemberQuery:
    return GetServersWhereUserMemberQuery(server_repository=server_repository)


def get_server_where_user_member_query(
    server_repository: ServerRepositoryDep,
) -> GetServerWhereUserMemberQuery:
    return GetServerWhereUserMemberQuery(server_repository=server_repository)


def get_invites_query(
    server_repository: ServerRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
) -> GetInvitesQuery:
    return GetInvitesQuery(
        server_repository=server_repository,
        server_invite_repository=server_invite_repository,
    )


ServerRepositoryDep = Annotated[ServerRepository, Depends(get_server_repository)]
ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
ServerInviteRepositoryDep = Annotated[
    ServerInviteRepository, Depends(get_server_invite_repository)
]
ServerUnitOfWorkDep = Annotated[ServerUnitOfWork, Depends(get_server_unit_of_work)]
CreateServerCommandDep = Annotated[
    CreateServerCommand, Depends(get_create_server_command)
]
UpdateServerCommandDep = Annotated[
    UpdateServerCommand, Depends(get_update_server_command)
]
DeleteServerCommandDep = Annotated[
    DeleteServerCommand, Depends(get_delete_server_command)
]
TransferServerOwnershipCommandDep = Annotated[
    TransferServerOwnershipCommand, Depends(get_transfer_ownership_command)
]
JoinServerCommandDep = Annotated[JoinServerCommand, Depends(get_join_server_command)]
CreateInviteCommandDep = Annotated[
    CreateInviteCommand, Depends(get_create_invite_command)
]
DeleteInviteCommandDep = Annotated[
    DeleteInviteCommand, Depends(get_delete_invite_command)
]
GetServersWhereUserMemberQueryDep = Annotated[
    GetServersWhereUserMemberQuery, Depends(get_servers_where_user_member_query)
]
GetServerWhereUserMemberQueryDep = Annotated[
    GetServerWhereUserMemberQuery, Depends(get_server_where_user_member_query)
]
GetInvitesQueryDep = Annotated[GetInvitesQuery, Depends(get_invites_query)]
