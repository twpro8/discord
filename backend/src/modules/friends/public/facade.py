from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.friends.domain.repositories.friend_repository import FriendRepository
from src.modules.friends.infrastructure.persistence.friend_repository_impl import (
    FriendRepositoryImpl,
)


class FriendsFacade(Protocol):
    """The only way other modules may read a user's friend list. Returns
    bare ids, not entities/DTOs with user info — callers that need more
    than "who to notify" should go through `users`' own facade for the
    ids returned here."""

    async def list_friend_ids(self, user_id: UUID) -> set[UUID]: ...


class RepositoryBackedFriendsFacade:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def list_friend_ids(self, user_id: UUID) -> set[UUID]:
        return await self._friends.list_friend_ids(user_id)


def build_friends_facade(session: AsyncSession) -> FriendsFacade:
    return RepositoryBackedFriendsFacade(FriendRepositoryImpl(session))
