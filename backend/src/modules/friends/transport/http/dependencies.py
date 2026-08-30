from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import CacheDep, SessionDep, TransactionDep
from src.modules.friends.adapters.persistence.friend_repository_impl import (
    FriendRepositoryImpl,
)
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.modules.friends.usecases.accept_request import AcceptFriendRequestUseCase
from src.modules.friends.usecases.delete_request import DeleteFriendRequestUseCase
from src.modules.friends.usecases.get_friends import GetFriendsUseCase
from src.modules.friends.usecases.get_requests import GetFriendRequestsUseCase
from src.modules.friends.usecases.get_sent_requests import GetSentFriendRequestsUseCase
from src.modules.friends.usecases.remove_friend import RemoveFriendUseCase
from src.modules.friends.usecases.send_request import SendFriendRequestUseCase
from src.modules.users.public.facade import UsersFacade, build_users_facade


def get_friend_repository(session: SessionDep) -> FriendRepository:
    return FriendRepositoryImpl(session)


def get_users_facade(session: SessionDep, cache: CacheDep) -> UsersFacade:
    return build_users_facade(session, cache)


FriendRepositoryDep = Annotated[FriendRepository, Depends(get_friend_repository)]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]


async def get_send_friend_request_use_case(
    friend_repository: FriendRepositoryDep,
    users_facade: UsersFacadeDep,
    _tx: TransactionDep,
) -> SendFriendRequestUseCase:
    return SendFriendRequestUseCase(friend_repository, users_facade)


async def get_accept_friend_request_use_case(
    friend_repository: FriendRepositoryDep, _tx: TransactionDep
) -> AcceptFriendRequestUseCase:
    return AcceptFriendRequestUseCase(friend_repository)


async def get_delete_friend_request_use_case(
    friend_repository: FriendRepositoryDep, _tx: TransactionDep
) -> DeleteFriendRequestUseCase:
    return DeleteFriendRequestUseCase(friend_repository)


async def get_remove_friend_use_case(
    friend_repository: FriendRepositoryDep, _tx: TransactionDep
) -> RemoveFriendUseCase:
    return RemoveFriendUseCase(friend_repository)


async def get_get_friends_use_case(
    friend_repository: FriendRepositoryDep,
) -> GetFriendsUseCase:
    return GetFriendsUseCase(friend_repository)


async def get_get_friend_requests_use_case(
    friend_repository: FriendRepositoryDep,
) -> GetFriendRequestsUseCase:
    return GetFriendRequestsUseCase(friend_repository)


async def get_get_sent_friend_requests_use_case(
    friend_repository: FriendRepositoryDep,
) -> GetSentFriendRequestsUseCase:
    return GetSentFriendRequestsUseCase(friend_repository)


SendFriendRequestUseCaseDep = Annotated[
    SendFriendRequestUseCase, Depends(get_send_friend_request_use_case)
]
AcceptFriendRequestUseCaseDep = Annotated[
    AcceptFriendRequestUseCase, Depends(get_accept_friend_request_use_case)
]
DeleteFriendRequestUseCaseDep = Annotated[
    DeleteFriendRequestUseCase, Depends(get_delete_friend_request_use_case)
]
RemoveFriendUseCaseDep = Annotated[
    RemoveFriendUseCase, Depends(get_remove_friend_use_case)
]
GetFriendsUseCaseDep = Annotated[GetFriendsUseCase, Depends(get_get_friends_use_case)]
GetFriendRequestsUseCaseDep = Annotated[
    GetFriendRequestsUseCase, Depends(get_get_friend_requests_use_case)
]
GetSentFriendRequestsUseCaseDep = Annotated[
    GetSentFriendRequestsUseCase, Depends(get_get_sent_friend_requests_use_case)
]
