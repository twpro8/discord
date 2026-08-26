from collections.abc import AsyncGenerator
from contextlib import aclosing
from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies import CacheDep, EventBusDep, SessionDep
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.modules.friends.infrastructure.friend_unit_of_work_impl import (
    FriendUnitOfWorkImpl,
)
from src.modules.friends.infrastructure.persistence.friend_repository_impl import (
    FriendRepositoryImpl,
)
from src.modules.friends.usecases.accept_request import AcceptFriendRequestUseCase
from src.modules.friends.usecases.delete_request import DeleteFriendRequestUseCase
from src.modules.friends.usecases.get_friends import GetFriendsUseCase
from src.modules.friends.usecases.get_requests import GetFriendRequestsUseCase
from src.modules.friends.usecases.get_sent_requests import GetSentFriendRequestsUseCase
from src.modules.friends.usecases.remove_friend import RemoveFriendUseCase
from src.modules.friends.usecases.send_request import SendFriendRequestUseCase
from src.modules.users.public.facade import UsersFacade, build_users_facade


async def get_friend_unit_of_work(
    session: SessionDep,
) -> AsyncGenerator[FriendUnitOfWork]:
    friend_repository = FriendRepositoryImpl(session)
    async with FriendUnitOfWorkImpl(session, friend_repository) as uow:
        yield uow


async def get_users_facade(
    session: SessionDep, cache: CacheDep, event_bus: EventBusDep
) -> AsyncGenerator[UsersFacade]:
    async with aclosing(build_users_facade(session, cache, event_bus)) as facades:
        async for facade in facades:
            yield facade


FriendUnitOfWorkDep = Annotated[FriendUnitOfWork, Depends(get_friend_unit_of_work)]
UsersFacadeDep = Annotated[UsersFacade, Depends(get_users_facade)]


async def get_send_friend_request_use_case(
    uow: FriendUnitOfWorkDep, users_facade: UsersFacadeDep
) -> SendFriendRequestUseCase:
    return SendFriendRequestUseCase(uow, users_facade)


async def get_accept_friend_request_use_case(
    uow: FriendUnitOfWorkDep,
) -> AcceptFriendRequestUseCase:
    return AcceptFriendRequestUseCase(uow)


async def get_delete_friend_request_use_case(
    uow: FriendUnitOfWorkDep,
) -> DeleteFriendRequestUseCase:
    return DeleteFriendRequestUseCase(uow)


async def get_remove_friend_use_case(uow: FriendUnitOfWorkDep) -> RemoveFriendUseCase:
    return RemoveFriendUseCase(uow)


async def get_get_friends_use_case(uow: FriendUnitOfWorkDep) -> GetFriendsUseCase:
    return GetFriendsUseCase(uow.friends)


async def get_get_friend_requests_use_case(
    uow: FriendUnitOfWorkDep,
) -> GetFriendRequestsUseCase:
    return GetFriendRequestsUseCase(uow.friends)


async def get_get_sent_friend_requests_use_case(
    uow: FriendUnitOfWorkDep,
) -> GetSentFriendRequestsUseCase:
    return GetSentFriendRequestsUseCase(uow.friends)


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
