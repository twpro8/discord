from dataclasses import dataclass
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.rooms import server_room
from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.shared.application.query import Query
from src.shared.result import Result

logger = get_logger(__name__)


@dataclass(frozen=True, kw_only=True)
class GetServerWhereUserMemberQuery(Query):
    user_id: UUID
    server_id: UUID


class GetServerWhereUserMemberQueryHandler:
    def __init__(
        self,
        server_repository: ServerRepository,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._server_repository = server_repository
        self._room_membership_updater = room_membership_updater

    async def handle(
        self, query: GetServerWhereUserMemberQuery
    ) -> Result[Server, ServerNotFoundError]:
        result = await self._server_repository.get_server_where_user_is_member(
            user_id=query.user_id,
            server_id=query.server_id,
        )

        if not result:
            return Result.err(ServerNotFoundError())

        # Lazy join-on-view, mirroring messages.application.queries.
        # list_chat_messages: a connection that predates the user opening
        # this server still gets its room membership here rather than at
        # connect time. Best effort: this is realtime delivery plumbing,
        # not the read the caller actually asked for.
        try:
            await self._room_membership_updater.join_user_to_room(
                query.user_id, server_room(query.server_id)
            )
        except Exception:
            logger.exception(
                "realtime.room_join_failed",
                user_id=str(query.user_id),
                server_id=str(query.server_id),
            )

        return Result.ok(result)
