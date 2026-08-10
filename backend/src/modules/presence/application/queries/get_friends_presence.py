from dataclasses import dataclass
from uuid import UUID

from src.modules.friends.public.facade import FriendsFacade
from src.modules.presence.domain.entities.dtos import PresenceDTO
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetFriendsPresenceQuery(Query):
    user_id: UUID


class GetFriendsPresenceQueryHandler:
    def __init__(
        self,
        presence_repository: PresenceRepository,
        friends_facade: FriendsFacade,
    ) -> None:
        self._presence = presence_repository
        self._friends_facade = friends_facade

    async def handle(
        self, query: GetFriendsPresenceQuery
    ) -> Result[list[PresenceDTO], LumiereError]:
        friend_ids = await self._friends_facade.list_friend_ids(query.user_id)
        statuses = await self._presence.get_statuses(friend_ids)
        return Result.ok(list(statuses.values()))
