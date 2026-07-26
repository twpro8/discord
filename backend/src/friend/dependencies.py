"""FastAPI dependencies for friend request operations."""

# Python modules
from collections.abc import AsyncGenerator
from typing import Annotated

# Third-party modules
from fastapi import Depends

# Project modules
from src.core.dependencies import SessionDep
from src.friend.repository import FriendRepository
from src.friend.service import FriendService
from src.friend.unit_of_work import FriendUnitOfWork
from src.user.repository import UserRepository


def get_friend_repository(session: SessionDep) -> FriendRepository:
    """Provide a friend repository bound to the request session."""
    return FriendRepository(session)


async def get_friend_unit_of_work(
    session: SessionDep,
    friend_repository: FriendRepositoryDep,
) -> AsyncGenerator[FriendUnitOfWork]:
    """Provide a transactional unit of work for a friend request."""
    user_repository = UserRepository(session)
    async with FriendUnitOfWork(
        session,
        friend_repository,
        user_repository,
    ) as friend_unit_of_work:
        yield friend_unit_of_work


def get_friend_service(friend_unit_of_work: FriendUnitOfWorkDep) -> FriendService:
    """Provide the friend request application service."""
    return FriendService(friend_unit_of_work)


FriendRepositoryDep = Annotated[FriendRepository, Depends(get_friend_repository)]
FriendUnitOfWorkDep = Annotated[FriendUnitOfWork, Depends(get_friend_unit_of_work)]
FriendServiceDep = Annotated[FriendService, Depends(get_friend_service)]
