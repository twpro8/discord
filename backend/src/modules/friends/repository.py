"""Database access for friend requests."""

# Python modules
from uuid import UUID

# Third-party modules
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from src.modules.friends.enums import FriendStatus
from src.modules.friends.mappers import FriendMapper
from src.modules.friends.models import FriendOrm
from src.modules.friends.schemas import FriendRequest, FriendRequestWithUser

# Project modules
from src.shared.repositories import BaseRepository


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

    async def get_by_id(self, request_id: UUID) -> FriendRequest | None:
        """Return a single relationship by its primary key."""
        return await self.get_one(id=request_id)

    async def get_for_user(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        """Return all friend relationships targeted at *user_id* for the given *status*."""
        statement = (
            select(self.model)
            .options(joinedload(self.model.user))
            .where(
                self.model.target_user_id == user_id,
                self.model.status == status,
            )
        )
        result = await self.session.execute(statement)
        orm_objects = result.scalars().unique().all()

        return [
            FriendRequestWithUser(
                id=obj.id,
                user_id=obj.user_id,
                target_user_id=obj.target_user_id,
                status=obj.status,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                username=obj.user.username,
                avatar_url=obj.user.avatar_url,
            )
            for obj in orm_objects
        ]

    async def get_user_sent_requests(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        """Return all friend relationships sent by the user with *user_id* for the given *status*."""
        statement = (
            select(self.model)
            .options(joinedload(self.model.target_user))
            .where(
                self.model.user_id == user_id,
                self.model.status == status,
            )
        )
        result = await self.session.execute(statement)
        orm_objects = result.scalars().unique().all()

        return [
            FriendRequestWithUser(
                id=obj.id,
                user_id=obj.user_id,
                target_user_id=obj.target_user_id,
                status=obj.status,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                username=obj.target_user.username,
                avatar_url=obj.target_user.avatar_url,
            )
            for obj in orm_objects
        ]

    async def get_friends(self, user_id: UUID) -> list[FriendRequestWithUser]:
        """Return all accepted friend relationships for the user in either direction."""
        statement = (
            select(self.model)
            .options(joinedload(self.model.user), joinedload(self.model.target_user))
            .where(
                or_(
                    self.model.user_id == user_id,
                    self.model.target_user_id == user_id,
                ),
                self.model.status == FriendStatus.FRIENDS,
            )
        )
        result = await self.session.execute(statement)
        orm_objects = result.scalars().unique().all()

        return [
            FriendRequestWithUser(
                id=obj.id,
                user_id=obj.user_id,
                target_user_id=obj.target_user_id,
                status=obj.status,
                created_at=obj.created_at,
                updated_at=obj.updated_at,
                username=(
                    obj.target_user.username
                    if obj.user_id == user_id
                    else obj.user.username
                ),
                avatar_url=(
                    obj.target_user.avatar_url
                    if obj.user_id == user_id
                    else obj.user.avatar_url
                ),
            )
            for obj in orm_objects
        ]
