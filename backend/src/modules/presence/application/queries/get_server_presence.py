from dataclasses import dataclass
from uuid import UUID

from src.modules.presence.domain.entities.dtos import PresenceDTO
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetServerPresenceQuery(Query):
    server_id: UUID
    requesting_user_id: UUID


class GetServerPresenceQueryHandler:
    def __init__(
        self,
        presence_repository: PresenceRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._presence = presence_repository
        self._servers_facade = servers_facade

    async def handle(
        self, query: GetServerPresenceQuery
    ) -> Result[list[PresenceDTO], LumiereError]:
        try:
            await self._servers_facade.assert_is_server_member(
                query.requesting_user_id, query.server_id
            )
        except LumiereError as error:
            return Result.err(error)

        member_ids = await self._servers_facade.list_server_member_ids(query.server_id)
        statuses = await self._presence.get_statuses(member_ids)
        return Result.ok(list(statuses.values()))
