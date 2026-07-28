from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import SessionDep
from src.modules.friends.application.commands.accept_request import (
    AcceptFriendRequestCommand,
)
from src.modules.friends.application.commands.delete_request import (
    DeleteFriendRequestCommand,
)
from src.modules.friends.application.commands.remove_friend import RemoveFriendCommand
from src.modules.friends.application.commands.send_request import (
    SendFriendRequestCommand,
)
from src.modules.friends.application.queries.get_friends import GetFriendsQuery
from src.modules.friends.application.queries.get_requests import (
    GetFriendRequestsQuery,
)
from src.modules.friends.application.queries.get_sent_requests import (
    GetSentFriendRequestsQuery,
)
from src.modules.friends.infrastructure.persistence.repository import FriendRepository
from src.modules.friends.infrastructure.unit_of_work import FriendUnitOfWork
from src.modules.users.infrastructure.persistence.repository import (
    SqlAlchemyUserRepository,
)


def get_friend_repository(session: SessionDep) -> FriendRepository:
    return FriendRepository(session)


async def get_friend_unit_of_work(
    session: SessionDep,
    friend_repository: FriendRepositoryDep,
) -> AsyncGenerator[FriendUnitOfWork]:
    user_repository = SqlAlchemyUserRepository(session)
    async with FriendUnitOfWork(
        session,
        friend_repository,
        user_repository,
    ) as friend_unit_of_work:
        yield friend_unit_of_work


def get_send_friend_request_command(
    uow: FriendUnitOfWorkDep,
) -> SendFriendRequestCommand:
    return SendFriendRequestCommand(uow)


def get_accept_friend_request_command(
    uow: FriendUnitOfWorkDep,
) -> AcceptFriendRequestCommand:
    return AcceptFriendRequestCommand(uow)


def get_delete_friend_request_command(
    uow: FriendUnitOfWorkDep,
) -> DeleteFriendRequestCommand:
    return DeleteFriendRequestCommand(uow)


def get_remove_friend_command(
    uow: FriendUnitOfWorkDep,
) -> RemoveFriendCommand:
    return RemoveFriendCommand(uow)


def get_friend_requests_query(
    friend_repository: FriendRepositoryDep,
) -> GetFriendRequestsQuery:
    return GetFriendRequestsQuery(friend_repository)


def get_sent_requests_query(
    friend_repository: FriendRepositoryDep,
) -> GetSentFriendRequestsQuery:
    return GetSentFriendRequestsQuery(friend_repository)


def get_friends_query(
    friend_repository: FriendRepositoryDep,
) -> GetFriendsQuery:
    return GetFriendsQuery(friend_repository)


FriendRepositoryDep = Annotated[FriendRepository, Depends(get_friend_repository)]
FriendUnitOfWorkDep = Annotated[FriendUnitOfWork, Depends(get_friend_unit_of_work)]
SendFriendRequestCommandDep = Annotated[
    SendFriendRequestCommand, Depends(get_send_friend_request_command)
]
AcceptFriendRequestCommandDep = Annotated[
    AcceptFriendRequestCommand, Depends(get_accept_friend_request_command)
]
DeleteFriendRequestCommandDep = Annotated[
    DeleteFriendRequestCommand, Depends(get_delete_friend_request_command)
]
RemoveFriendCommandDep = Annotated[
    RemoveFriendCommand, Depends(get_remove_friend_command)
]
GetFriendRequestsQueryDep = Annotated[
    GetFriendRequestsQuery, Depends(get_friend_requests_query)
]
GetSentFriendRequestsQueryDep = Annotated[
    GetSentFriendRequestsQuery, Depends(get_sent_requests_query)
]
GetFriendsQueryDep = Annotated[GetFriendsQuery, Depends(get_friends_query)]
