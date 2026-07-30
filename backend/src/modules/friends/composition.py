from contextlib import AsyncExitStack

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.application.commands.accept_request import (
    AcceptFriendRequestCommand,
    AcceptFriendRequestCommandHandler,
)
from src.modules.friends.application.commands.delete_request import (
    DeleteFriendRequestCommand,
    DeleteFriendRequestCommandHandler,
)
from src.modules.friends.application.commands.remove_friend import (
    RemoveFriendCommand,
    RemoveFriendCommandHandler,
)
from src.modules.friends.application.commands.send_request import (
    SendFriendRequestCommand,
    SendFriendRequestCommandHandler,
)
from src.modules.friends.application.queries.get_friends import (
    GetFriendsQuery,
    GetFriendsQueryHandler,
)
from src.modules.friends.application.queries.get_requests import (
    GetFriendRequestsQuery,
    GetFriendRequestsQueryHandler,
)
from src.modules.friends.application.queries.get_sent_requests import (
    GetSentFriendRequestsQuery,
    GetSentFriendRequestsQueryHandler,
)
from src.modules.friends.infrastructure.friend_unit_of_work_impl import (
    FriendUnitOfWorkImpl,
)
from src.modules.friends.infrastructure.persistence.friend_repository_impl import (
    FriendRepositoryImpl,
)
from src.modules.users.public.facade import UsersFacade
from src.shared.application.in_process_mediator import InProcessMediator


async def register_friend_handlers(
    mediator: InProcessMediator,
    session: AsyncSession,
    stack: AsyncExitStack,
    users_facade: UsersFacade,
) -> None:
    friend_repository = FriendRepositoryImpl(session)
    uow = await stack.enter_async_context(
        FriendUnitOfWorkImpl(session, friend_repository)
    )

    mediator.register_command(
        SendFriendRequestCommand,
        SendFriendRequestCommandHandler(uow, users_facade),
    )
    mediator.register_command(
        AcceptFriendRequestCommand, AcceptFriendRequestCommandHandler(uow)
    )
    mediator.register_command(
        DeleteFriendRequestCommand, DeleteFriendRequestCommandHandler(uow)
    )
    mediator.register_command(RemoveFriendCommand, RemoveFriendCommandHandler(uow))

    mediator.register_query(GetFriendsQuery, GetFriendsQueryHandler(friend_repository))
    mediator.register_query(
        GetFriendRequestsQuery, GetFriendRequestsQueryHandler(friend_repository)
    )
    mediator.register_query(
        GetSentFriendRequestsQuery,
        GetSentFriendRequestsQueryHandler(friend_repository),
    )
