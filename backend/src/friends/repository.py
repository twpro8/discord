"""Database access for friend requests."""

# Python modules
from uuid import UUID

# Third-party modules
from sqlalchemy import or_, select

# Project modules
from src.core.repositories import BaseRepository
from src.friends.mappers import FriendMapper
from src.friends.models import FriendOrm
from src.friends.schemas import FriendRequest


class FriendRepository(BaseRepository[FriendOrm, FriendRequest]):
    """Read and write friend relationship records."""

    model = FriendOrm
    mapper = FriendMapper

    async def get_between_users(
        self,
        first_user_id: UUID,
        second_user_id: UUID,
    ) -> FriendRequest | None:
        """Return an existing relationship in either direction, if present."""
        statement = select(self.model).where(
            or_(
                (self.model.user_id == first_user_id)
                & (self.model.target_user_id == second_user_id),
                (self.model.user_id == second_user_id)
                & (self.model.target_user_id == first_user_id),
            )
        )
        return await self._execute_and_map_one_or_none(statement)
