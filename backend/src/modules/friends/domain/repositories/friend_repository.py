from typing import Protocol
from uuid import UUID

from pydantic import BaseModel

from src.modules.friends.domain.entities.schemas import (
    FriendRequest,
    FriendRequestWithUser,
)
from src.modules.friends.domain.enums import FriendStatus


class FriendRepository(Protocol):
    async def create(self, data: BaseModel) -> FriendRequest: ...

    async def get_one(self, **filter_by: object) -> FriendRequest | None: ...

    async def get_between_users(
        self, first_user_id: UUID, second_user_id: UUID
    ) -> FriendRequest | None: ...

    async def get_by_id(self, request_id: UUID) -> FriendRequest | None: ...

    async def get_for_user(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]: ...

    async def get_user_sent_requests(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]: ...

    async def get_friends(self, user_id: UUID) -> list[FriendRequestWithUser]: ...

    async def update(
        self, id_: UUID, data: BaseModel, exclude_unset: bool = False
    ) -> FriendRequest: ...

    async def delete(self, id_: UUID) -> None: ...
