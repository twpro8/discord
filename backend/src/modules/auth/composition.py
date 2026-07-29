from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

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
from src.modules.auth.infrastructure.auth_unit_of_work_impl import AuthUnitOfWork
from src.modules.auth.infrastructure.persistence.refresh_token_repository_impl import (
    RefreshTokenRepositoryImpl,
)
from src.modules.users.infrastructure.persistence.repository import (
    UserRepositoryImpl,
)
from src.shared.application.in_process_mediator import InProcessMediator


async def register_auth_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    user_repository = UserRepositoryImpl(session)
    refresh_token_repository = RefreshTokenRepositoryImpl(session)
    uow = await stack.enter_async_context(
        AuthUnitOfWork(session, user_repository, refresh_token_repository)
    )

    mediator.register_command(LoginCommand, LoginCommandHandler(uow))
    mediator.register_command(RegisterCommand, RegisterCommandHandler(uow))
    mediator.register_command(RefreshCommand, RefreshCommandHandler(uow))
    mediator.register_command(LogoutCommand, LogoutCommandHandler(uow))
