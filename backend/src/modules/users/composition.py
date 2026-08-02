from src.modules.users.application.commands.create_user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from src.modules.users.application.commands.delete_user import (
    DeleteUserCommand,
    DeleteUserCommandHandler,
)
from src.modules.users.application.commands.update_user import (
    UpdateUserCommand,
    UpdateUserCommandHandler,
)
from src.modules.users.application.queries.get_user_by_id import (
    GetUserByIDQuery,
    GetUserByIDQueryHandler,
)
from src.modules.users.application.queries.get_user_by_username import (
    GetUserByUsernameQuery,
    GetUserByUsernameQueryHandler,
)
from src.modules.users.application.queries.verify_credentials import (
    VerifyCredentialsQuery,
    VerifyCredentialsQueryHandler,
)
from src.modules.users.infrastructure.persistence.user_repository_impl import (
    UserRepositoryImpl,
)
from src.modules.users.infrastructure.user_unit_of_work_impl import (
    UserUnitOfWorkImpl,
)
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> UserUnitOfWorkImpl:
    return UserUnitOfWorkImpl(services.session, UserRepositoryImpl(services.session))


def _build_create_user_handler(
    services: RequestServices, _mediator: Mediator
) -> CreateUserCommandHandler:
    return CreateUserCommandHandler(_build_uow(services), services.event_bus)


def _build_update_user_handler(
    services: RequestServices, _mediator: Mediator
) -> UpdateUserCommandHandler:
    return UpdateUserCommandHandler(_build_uow(services), services.cache)


def _build_delete_user_handler(
    services: RequestServices, _mediator: Mediator
) -> DeleteUserCommandHandler:
    return DeleteUserCommandHandler(_build_uow(services), services.cache)


def _build_get_user_by_id_handler(
    services: RequestServices, _mediator: Mediator
) -> GetUserByIDQueryHandler:
    return GetUserByIDQueryHandler(UserRepositoryImpl(services.session), services.cache)


def _build_get_user_by_username_handler(
    services: RequestServices, _mediator: Mediator
) -> GetUserByUsernameQueryHandler:
    return GetUserByUsernameQueryHandler(UserRepositoryImpl(services.session))


def _build_verify_credentials_handler(
    services: RequestServices, _mediator: Mediator
) -> VerifyCredentialsQueryHandler:
    return VerifyCredentialsQueryHandler(UserRepositoryImpl(services.session))


def register_user_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(CreateUserCommand, _build_create_user_handler)
    registry.register_command_factory(UpdateUserCommand, _build_update_user_handler)
    registry.register_command_factory(DeleteUserCommand, _build_delete_user_handler)
    registry.register_query_factory(GetUserByIDQuery, _build_get_user_by_id_handler)
    registry.register_query_factory(
        GetUserByUsernameQuery, _build_get_user_by_username_handler
    )
    registry.register_query_factory(
        VerifyCredentialsQuery, _build_verify_credentials_handler
    )
