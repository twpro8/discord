from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.domain.entities.dtos import FriendRequestWithUser
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetFriendsQuery(Query):
    user_id: UUID


class GetFriendsQueryHandler:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def handle(
        self, query: GetFriendsQuery
    ) -> Result[list[FriendRequestWithUser], LumiereError]:
        friends = await self._friends.get_friends(query.user_id)
        return Result.ok(friends)
