from contextlib import AsyncExitStack, asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.channels.public.facade import build_channels_facade
from src.modules.servers.application.commands.create_invite import (
    CreateInviteCommand,
    CreateInviteCommandHandler,
)
from src.modules.servers.application.commands.create_server import (
    CreateServerCommand,
    CreateServerCommandHandler,
)
from src.modules.servers.application.commands.delete_invite import (
    DeleteInviteCommand,
    DeleteInviteCommandHandler,
)
from src.modules.servers.application.commands.delete_server import (
    DeleteServerCommand,
    DeleteServerCommandHandler,
)
from src.modules.servers.application.commands.join_server import (
    JoinServerCommand,
    JoinServerCommandHandler,
)
from src.modules.servers.application.commands.transfer_ownership import (
    TransferServerOwnershipCommand,
    TransferServerOwnershipCommandHandler,
)
from src.modules.servers.application.commands.update_server import (
    UpdateServerCommand,
    UpdateServerCommandHandler,
)
from src.modules.servers.application.queries.get_invites import (
    GetInvitesQuery,
    GetInvitesQueryHandler,
)
from src.modules.servers.application.queries.get_server_members import (
    GetServerMembersQuery,
    GetServerMembersQueryHandler,
)
from src.modules.servers.application.queries.get_server_where_user_member import (
    GetServerWhereUserMemberQuery,
    GetServerWhereUserMemberQueryHandler,
)
from src.modules.servers.application.queries.get_servers_where_user_member import (
    GetServersWhereUserMemberQuery,
    GetServersWhereUserMemberQueryHandler,
)
from src.modules.servers.infrastructure.persistence.server_invite_repository_impl import (
    ServerInviteRepositoryImpl,
)
from src.modules.servers.infrastructure.persistence.server_member_repository_impl import (
    ServerMemberRepositoryImpl,
)
from src.modules.servers.infrastructure.persistence.server_repository_impl import (
    ServerRepositoryImpl,
)
from src.modules.servers.infrastructure.server_unit_of_work_impl import (
    ServerUnitOfWorkImpl,
)
from src.shared.application.in_process_mediator import InProcessMediator


async def register_server_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
    room_membership_updater: RoomMembershipUpdater,
) -> None:
    server_repository = ServerRepositoryImpl(session=session)
    server_member_repository = ServerMemberRepositoryImpl(session=session)
    server_invite_repository = ServerInviteRepositoryImpl(session=session)
    uow = await stack.enter_async_context(
        ServerUnitOfWorkImpl(
            session,
            server_repository,
            server_member_repository,
            server_invite_repository,
        )
    )

    # CreateServerCommandHandler delegates default-channel creation to
    # channels as part of its own atomic operation (not via mediator.send()),
    # so it needs a same-session facade rather than a mediator registration.
    channels_facade = await stack.enter_async_context(
        asynccontextmanager(build_channels_facade)(session)
    )

    mediator.register_command(
        CreateServerCommand,
        CreateServerCommandHandler(uow, channels_facade, room_membership_updater),
    )
    mediator.register_command(UpdateServerCommand, UpdateServerCommandHandler(uow))
    mediator.register_command(DeleteServerCommand, DeleteServerCommandHandler(uow))
    mediator.register_command(
        TransferServerOwnershipCommand, TransferServerOwnershipCommandHandler(uow)
    )
    mediator.register_command(
        JoinServerCommand, JoinServerCommandHandler(uow, room_membership_updater)
    )
    mediator.register_command(CreateInviteCommand, CreateInviteCommandHandler(uow))
    mediator.register_command(DeleteInviteCommand, DeleteInviteCommandHandler(uow))

    mediator.register_query(
        GetServersWhereUserMemberQuery,
        GetServersWhereUserMemberQueryHandler(server_repository),
    )
    mediator.register_query(
        GetServerWhereUserMemberQuery,
        GetServerWhereUserMemberQueryHandler(
            server_repository, room_membership_updater
        ),
    )
    mediator.register_query(
        GetInvitesQuery,
        GetInvitesQueryHandler(server_repository, server_invite_repository),
    )
    mediator.register_query(
        GetServerMembersQuery,
        GetServerMembersQueryHandler(server_member_repository),
    )
