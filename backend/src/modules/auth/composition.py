from src.modules.auth.application.commands.login import (
    LoginCommand,
    LoginCommandHandler,
)
from src.modules.auth.application.commands.logout import (
    LogoutCommand,
    LogoutCommandHandler,
)
from src.modules.auth.application.commands.refresh import (
    RefreshCommand,
    RefreshCommandHandler,
)
from src.modules.auth.application.commands.register import (
    RegisterCommand,
    RegisterCommandHandler,
)
from src.modules.auth.infrastructure.auth_unit_of_work_impl import AuthUnitOfWorkImpl
from src.modules.auth.infrastructure.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.modules.users.public.facade import MediatorUsersFacade
from src.shared.application.handler_registry import HandlerRegistry, RequestServices
from src.shared.application.mediator import Mediator


def _build_uow(services: RequestServices) -> AuthUnitOfWorkImpl:
    return AuthUnitOfWorkImpl(
        services.session, RefreshTokenRepositoryImpl(services.session)
    )


def _build_login_handler(
    services: RequestServices, mediator: Mediator
) -> LoginCommandHandler:
    return LoginCommandHandler(_build_uow(services), MediatorUsersFacade(mediator))


def _build_register_handler(
    _services: RequestServices, mediator: Mediator
) -> RegisterCommandHandler:
    return RegisterCommandHandler(MediatorUsersFacade(mediator))


def _build_refresh_handler(
    services: RequestServices, _mediator: Mediator
) -> RefreshCommandHandler:
    return RefreshCommandHandler(_build_uow(services))


def _build_logout_handler(
    services: RequestServices, _mediator: Mediator
) -> LogoutCommandHandler:
    return LogoutCommandHandler(_build_uow(services))


def register_auth_handlers(registry: HandlerRegistry) -> None:
    registry.register_command_factory(LoginCommand, _build_login_handler)
    registry.register_command_factory(RegisterCommand, _build_register_handler)
    registry.register_command_factory(RefreshCommand, _build_refresh_handler)
    registry.register_command_factory(LogoutCommand, _build_logout_handler)
