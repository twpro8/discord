from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel

from src.modules.friends.domain.entities.schemas import (
    FriendRequest,
    FriendRequestCreate,
    FriendRequestUpdate,
    FriendRequestWithUser,
)
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.repositories.friend_unit_of_work import (
    FriendUnitOfWork,
)
from src.modules.users.domain.entities.user import User


def make_user(username: str, is_active: bool = True) -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid4(),
        name=username,
        username=username,
        email=f"{username}@test.com",
        password_hash="hash",
        avatar_url=None,
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


class FakeFriendRepository:
    def __init__(self) -> None:
        self.requests: dict[UUID, FriendRequest] = {}
        self.requests_for_user: list[FriendRequestWithUser] = []
        self.sent_requests: list[FriendRequestWithUser] = []
        self.friends_list: list[FriendRequestWithUser] = []

    async def create(self, data: FriendRequestCreate) -> FriendRequest:
        now = datetime.now(UTC)
        request = FriendRequest(
            id=uuid4(),
            user_id=data.user_id,
            target_user_id=data.target_user_id,
            status=data.status,
            created_at=now,
            updated_at=now,
        )
        self.requests[request.id] = request
        return request

    async def get_between_users(
        self,
        first_user_id: UUID,
        second_user_id: UUID,
    ) -> FriendRequest | None:
        for request in self.requests.values():
            if {request.user_id, request.target_user_id} == {
                first_user_id,
                second_user_id,
            }:
                return request
        return None

    async def get_by_id(self, request_id: UUID) -> FriendRequest | None:
        return self.requests.get(request_id)

    async def get_for_user(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        return self.requests_for_user

    async def get_user_sent_requests(
        self,
        user_id: UUID,
        status: FriendStatus = FriendStatus.PENDING,
    ) -> list[FriendRequestWithUser]:
        return self.sent_requests

    async def get_friends(self, user_id: UUID) -> list[FriendRequestWithUser]:
        return self.friends_list

    async def update(
        self,
        request_id: UUID,
        data: FriendRequestUpdate,
        exclude_unset: bool = False,
    ) -> FriendRequest:
        request = self.requests[request_id]
        request.status = data.status
        request.updated_at = datetime.now(UTC)
        return request

    async def delete(self, request_id: UUID) -> None:
        self.requests.pop(request_id, None)


class FakeUserRepository:
    def __init__(self, users: list[User] | None = None) -> None:
        self.users: dict[UUID, User] = {u.id: u for u in (users or [])}

    async def create(self, data: BaseModel) -> User:
        raise NotImplementedError

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def get_by_username(self, username: str) -> User | None:
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    async def update(
        self,
        user_id: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
    ) -> User:
        raise NotImplementedError


class FakeFriendUnitOfWork(FriendUnitOfWork):
    def __init__(
        self,
        friends: FakeFriendRepository,
        users: FakeUserRepository,
    ) -> None:
        self.friends = friends
        self.users = users
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
