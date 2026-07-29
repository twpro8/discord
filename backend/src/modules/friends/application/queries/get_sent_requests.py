from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.domain.entities.schemas import FriendRequestWithUser
from src.modules.friends.domain.enums import FriendStatus
from src.modules.friends.domain.repositories.friend_repository import (
    FriendRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetSentFriendRequestsQuery(Query):
    user_id: UUID
    status: FriendStatus = FriendStatus.PENDING


class GetSentFriendRequestsQueryHandler:
    def __init__(self, friend_repository: FriendRepository) -> None:
        self._friends = friend_repository

    async def handle(
        self, query: GetSentFriendRequestsQuery
    ) -> Result[list[FriendRequestWithUser], LumiereError]:
        requests = await self._friends.get_user_sent_requests(
            query.user_id, query.status
        )
        return Result.ok(requests)
