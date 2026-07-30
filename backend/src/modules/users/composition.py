from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

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
from src.modules.users.infrastructure.persistence.repository import (
    UserRepositoryImpl,
)
from src.modules.users.infrastructure.unit_of_work import UserUnitOfWork
from src.shared.application.in_process_mediator import InProcessMediator


async def register_user_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
) -> None:
    user_repository = UserRepositoryImpl(session)
    uow = await stack.enter_async_context(UserUnitOfWork(session, user_repository))

    mediator.register_command(UpdateUserCommand, UpdateUserCommandHandler(uow))
    mediator.register_command(DeleteUserCommand, DeleteUserCommandHandler(uow))
    mediator.register_query(GetUserByIDQuery, GetUserByIDQueryHandler(user_repository))
