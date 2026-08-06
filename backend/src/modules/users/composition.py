from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cache import Cache
from src.core.event_bus import EventBus
from src.core.storage import Storage
from src.modules.users.application.commands.change_password import (
    ChangePasswordCommand,
    ChangePasswordCommandHandler,
)
from src.modules.users.application.commands.create_user import (
    CreateUserCommand,
    CreateUserCommandHandler,
)
from src.modules.users.application.commands.delete_user import (
    DeleteUserCommand,
    DeleteUserCommandHandler,
)
from src.modules.users.application.commands.update_avatar import (
    UpdateAvatarCommand,
    UpdateAvatarCommandHandler,
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
from src.shared.application.in_process_mediator import InProcessMediator


async def register_user_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
    event_bus: EventBus,
    cache: Cache,
    storage: Storage | None,
) -> None:
    user_repository = UserRepositoryImpl(session)
    uow = await stack.enter_async_context(UserUnitOfWorkImpl(session, user_repository))

    mediator.register_command(UpdateUserCommand, UpdateUserCommandHandler(uow, cache))
    mediator.register_command(DeleteUserCommand, DeleteUserCommandHandler(uow, cache))
    mediator.register_command(
        CreateUserCommand, CreateUserCommandHandler(uow, event_bus)
    )
    mediator.register_command(
        ChangePasswordCommand, ChangePasswordCommandHandler(uow, cache)
    )
    mediator.register_command(
        UpdateAvatarCommand,
        UpdateAvatarCommandHandler(uow, cache, storage),
    )
    mediator.register_query(
        GetUserByIDQuery, GetUserByIDQueryHandler(user_repository, cache)
    )
    mediator.register_query(
        GetUserByUsernameQuery, GetUserByUsernameQueryHandler(user_repository)
    )
    mediator.register_query(
        VerifyCredentialsQuery, VerifyCredentialsQueryHandler(user_repository)
    )
