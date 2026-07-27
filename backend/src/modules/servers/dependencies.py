from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.channels.dependencies import ChannelServiceDep
from src.modules.servers.invites.repository import ServerInviteRepository
from src.modules.servers.invites.service import ServerInviteService
from src.modules.servers.invites.unit_of_work import ServerInviteUnitOfWork
from src.modules.servers.repository import ServerRepository
from src.modules.servers.server_members.repository import ServerMemberRepository
from src.modules.servers.server_members.service import ServerMemberService
from src.modules.servers.server_members.unit_of_work import ServerMemberUnitOfWork
from src.modules.servers.service import ServerService
from src.modules.servers.unit_of_work import ServerUnitOfWork


def get_server_repository(
    session: SessionDep,
) -> ServerRepository:
    return ServerRepository(session=session)


async def get_server_unit_of_work(
    session: SessionDep,
    server_repository: ServerRepositoryDep,
) -> AsyncGenerator[ServerUnitOfWork]:
    async with ServerUnitOfWork(session, server_repository) as server_unit_of_work:
        yield server_unit_of_work


def get_server_invite_repository(
    session: SessionDep,
) -> ServerInviteRepository:
    return ServerInviteRepository(session=session)


async def get_server_invite_unit_of_work(
    session: SessionDep,
    server_repository: ServerRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
) -> AsyncGenerator[ServerInviteUnitOfWork]:
    async with ServerInviteUnitOfWork(
        session,
        server_invite_repository,
        server_repository,
    ) as server_invite_unit_of_work:
        yield server_invite_unit_of_work


def get_server_invite_service(
    session: SessionDep,
    server_invite_unit_of_work: ServerInviteUnitOfWorkDep,
) -> ServerInviteService:
    return ServerInviteService(
        session=session,
        server_invite_unit_of_work=server_invite_unit_of_work,
    )


def get_server_member_repository(
    session: SessionDep,
) -> ServerMemberRepository:
    return ServerMemberRepository(session=session)


async def get_server_member_unit_of_work(
    session: SessionDep,
    server_member_repository: ServerMemberRepositoryDep,
    server_invite_repository: ServerInviteRepositoryDep,
    server_repository: ServerRepositoryDep,
) -> AsyncGenerator[ServerMemberUnitOfWork]:
    async with ServerMemberUnitOfWork(
        session=session,
        server_member_repository=server_member_repository,
        server_invite_repository=server_invite_repository,
        server_repository=server_repository,
    ) as server_member_unit_of_work:
        yield server_member_unit_of_work


def get_server_member_service(
    session: SessionDep,
    server_member_unit_of_work: ServerMemberUnitOfWorkDep,
) -> ServerMemberService:
    return ServerMemberService(
        session=session,
        server_member_unit_of_work=server_member_unit_of_work,
    )


def get_server_service(
    session: SessionDep,
    server_unit_of_work: ServerUnitOfWorkDep,
    channel_service: ChannelServiceDep,
    server_member_service: ServerMemberServiceDep,
) -> ServerService:
    return ServerService(
        session=session,
        server_unit_of_work=server_unit_of_work,
        channel_service=channel_service,
        server_member_service=server_member_service,
    )


ServerRepositoryDep = Annotated[ServerRepository, Depends(get_server_repository)]
ServerInviteRepositoryDep = Annotated[
    ServerInviteRepository, Depends(get_server_invite_repository)
]
ServerMemberRepositoryDep = Annotated[
    ServerMemberRepository, Depends(get_server_member_repository)
]
ServerUnitOfWorkDep = Annotated[ServerUnitOfWork, Depends(get_server_unit_of_work)]
ServerInviteUnitOfWorkDep = Annotated[
    ServerInviteUnitOfWork, Depends(get_server_invite_unit_of_work)
]
ServerMemberUnitOfWorkDep = Annotated[
    ServerMemberUnitOfWork, Depends(get_server_member_unit_of_work)
]
ServerServiceDep = Annotated[ServerService, Depends(get_server_service)]
ServerInviteServiceDep = Annotated[
    ServerInviteService, Depends(get_server_invite_service)
]
ServerMemberServiceDep = Annotated[
    ServerMemberService, Depends(get_server_member_service)
]
