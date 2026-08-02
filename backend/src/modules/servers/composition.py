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
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> ServerUnitOfWorkImpl:
    return ServerUnitOfWorkImpl(
        services.session,
        ServerRepositoryImpl(session=services.session),
        ServerMemberRepositoryImpl(session=services.session),
        ServerInviteRepositoryImpl(session=services.session),
    )


def _build_create_server_handler(
    services: RequestServices, _mediator: Mediator
) -> CreateServerCommandHandler:
    # CreateServerCommandHandler delegates default-channel creation to
    # channels as part of its own atomic operation (not via mediator.send()),
    # so it needs a same-session facade rather than a mediator dispatch.
    channels_facade = build_channels_facade(services.session)
    return CreateServerCommandHandler(_build_uow(services), channels_facade)


def _build_update_server_handler(
    services: RequestServices, _mediator: Mediator
) -> UpdateServerCommandHandler:
    return UpdateServerCommandHandler(_build_uow(services))


def _build_delete_server_handler(
    services: RequestServices, _mediator: Mediator
) -> DeleteServerCommandHandler:
    return DeleteServerCommandHandler(_build_uow(services))


def _build_transfer_ownership_handler(
    services: RequestServices, _mediator: Mediator
) -> TransferServerOwnershipCommandHandler:
    return TransferServerOwnershipCommandHandler(_build_uow(services))


def _build_join_server_handler(
    services: RequestServices, _mediator: Mediator
) -> JoinServerCommandHandler:
    return JoinServerCommandHandler(_build_uow(services))


def _build_create_invite_handler(
    services: RequestServices, _mediator: Mediator
) -> CreateInviteCommandHandler:
    return CreateInviteCommandHandler(_build_uow(services))


def _build_delete_invite_handler(
    services: RequestServices, _mediator: Mediator
) -> DeleteInviteCommandHandler:
    return DeleteInviteCommandHandler(_build_uow(services))


def _build_get_servers_where_member_handler(
    services: RequestServices, _mediator: Mediator
) -> GetServersWhereUserMemberQueryHandler:
    return GetServersWhereUserMemberQueryHandler(
        ServerRepositoryImpl(session=services.session)
    )


def _build_get_server_where_member_handler(
    services: RequestServices, _mediator: Mediator
) -> GetServerWhereUserMemberQueryHandler:
    return GetServerWhereUserMemberQueryHandler(
        ServerRepositoryImpl(session=services.session)
    )


def _build_get_invites_handler(
    services: RequestServices, _mediator: Mediator
) -> GetInvitesQueryHandler:
    return GetInvitesQueryHandler(
        ServerRepositoryImpl(session=services.session),
        ServerInviteRepositoryImpl(session=services.session),
    )


def register_server_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(CreateServerCommand, _build_create_server_handler)
    registry.register_command_factory(UpdateServerCommand, _build_update_server_handler)
    registry.register_command_factory(DeleteServerCommand, _build_delete_server_handler)
    registry.register_command_factory(
        TransferServerOwnershipCommand, _build_transfer_ownership_handler
    )
    registry.register_command_factory(JoinServerCommand, _build_join_server_handler)
    registry.register_command_factory(CreateInviteCommand, _build_create_invite_handler)
    registry.register_command_factory(DeleteInviteCommand, _build_delete_invite_handler)

    registry.register_query_factory(
        GetServersWhereUserMemberQuery, _build_get_servers_where_member_handler
    )
    registry.register_query_factory(
        GetServerWhereUserMemberQuery, _build_get_server_where_member_handler
    )
    registry.register_query_factory(GetInvitesQuery, _build_get_invites_handler)
