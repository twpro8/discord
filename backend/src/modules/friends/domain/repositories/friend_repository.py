from typing import Protocol
from uuid import UUID

from src.modules.friends.domain.entities.dtos import (
    FriendRequestCreate,
    FriendRequestUpdate,
    FriendRequestWithUser,
)
from src.modules.friends.domain.entities.friend_request import FriendRequest
from src.modules.friends.domain.enums import FriendStatus


class FriendRepository(Protocol):
    async def create(self, data: FriendRequestCreate) -> FriendRequest: ...

    async def get_between_users(
        self,
        first_user_id: UUID,
        second_user_id: UUID,
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
        self,
        request_id: UUID,
        data: FriendRequestUpdate,
    ) -> FriendRequest: ...

    async def delete(self, request_id: UUID) -> None: ...
