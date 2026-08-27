from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.rooms import server_room
from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.domain.repositories.server_repository import ServerRepository

logger = get_logger(__name__)


class GetServerWhereUserMemberUseCase:
    def __init__(
        self,
        server_repository: ServerRepository,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._server_repository = server_repository
        self._room_membership_updater = room_membership_updater

    async def __call__(self, *, user_id: UUID, server_id: UUID) -> Server:
        result = await self._server_repository.get_server_where_user_is_member(
            user_id=user_id,
            server_id=server_id,
        )

        if not result:
            raise ServerNotFoundError

        # Lazy join-on-view, mirroring messages' list_chat_messages: a
        # connection that predates the user opening this server still
        # gets its room membership here rather than at connect time. Best
        # effort: this is realtime delivery plumbing, not the read the
        # caller actually asked for.
        try:
            await self._room_membership_updater.join_user_to_room(
                user_id, server_room(server_id)
            )
        except Exception:
            logger.exception(
                "realtime.room_join_failed",
                user_id=str(user_id),
                server_id=str(server_id),
            )

        return result
