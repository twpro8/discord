from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from src.modules.friends.adapters.persistence.mappers import (
    FriendRequestDataMapper,
)
from src.modules.friends.adapters.persistence.models import FriendOrm
from src.modules.friends.domain.entities.dtos import (
    FriendRequestCreate,
    FriendRequestUpdate,
    FriendRequestWithUser,
)
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.enums import FriendStatus
from src.shared.adapters.base_repository import BaseRepository


class FriendRepositoryImpl(
    BaseRepository[FriendOrm, FriendRequest, FriendRequestCreate, FriendRequestUpdate]
):
    _model = FriendOrm
    _mapper = FriendRequestDataMapper

    async def get_between_users(
        self,
        first_user_id: UUID,
        second_user_id: UUID,
    ) -> FriendRequest | None:
        """Return an existing relationship in either direction, if present."""
        stmt = select(FriendOrm).where(
            or_(
                (FriendOrm.user_id == first_user_id)
                & (FriendOrm.target_user_id == second_user_id),
                (FriendOrm.user_id == second_user_id)
                & (FriendOrm.target_user_id == first_user_id),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return FriendRequestDataMapper.to_entity(model) if model else None

    async def get_for_user(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        """Return all friend relationships targeted at *user_id* for the given *status*."""
        stmt = (
            select(FriendOrm)
            .options(joinedload(FriendOrm.user))
            .where(
                FriendOrm.target_user_id == user_id,
                FriendOrm.status == status,
            )
        )
        result = await self._session.execute(stmt)
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
        stmt = (
            select(FriendOrm)
            .options(joinedload(FriendOrm.target_user))
            .where(
                FriendOrm.user_id == user_id,
                FriendOrm.status == status,
            )
        )
        result = await self._session.execute(stmt)
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
        stmt = (
            select(FriendOrm)
            .options(joinedload(FriendOrm.user), joinedload(FriendOrm.target_user))
            .where(
                or_(
                    FriendOrm.user_id == user_id,
                    FriendOrm.target_user_id == user_id,
                ),
                FriendOrm.status == FriendStatus.FRIENDS,
            )
        )
        result = await self._session.execute(stmt)
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

    async def list_friend_ids(self, user_id: UUID) -> set[UUID]:
        """Lean id-only read for realtime fan-out (presence): avoids the
        username/avatar_url join `get_friends` does, since this runs on
        every presence transition."""
        stmt = select(FriendOrm.user_id, FriendOrm.target_user_id).where(
            or_(
                FriendOrm.user_id == user_id,
                FriendOrm.target_user_id == user_id,
            ),
            FriendOrm.status == FriendStatus.FRIENDS,
        )
        result = await self._session.execute(stmt)
        friend_ids: set[UUID] = set()
        for sent_by, sent_to in result.all():
            friend_ids.add(sent_to if sent_by == user_id else sent_by)
        return friend_ids
