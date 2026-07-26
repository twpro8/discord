"""Unit of work for friend request operations."""

# Third-party modules
from sqlalchemy.ext.asyncio import AsyncSession

# Project modules
from src.core.unit_of_work import BaseUnitOfWork
from src.modules.friend.repository import FriendRepository
from src.modules.user.repository import UserRepository


class FriendUnitOfWork(BaseUnitOfWork):
    """Expose repositories needed to create friend requests atomically."""

    def __init__(
        self,
        session: AsyncSession,
        friend_repository: FriendRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__(session)
        self.friends = friend_repository
        self.users = user_repository

    def _uow_marker(self) -> None:
        """Mark this as a concrete unit of work."""
