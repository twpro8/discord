from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.manager import RoomMembershipUpdater
from src.core.realtime.rooms import server_room

logger = get_logger(__name__)


async def join_members_to_server_room(
    room_membership_updater: RoomMembershipUpdater,
    server_id: UUID,
    member_ids: list[UUID],
) -> None:
    """Join each member's already-open connections (if any) to the
    server's room — mirrors chats' analogous join_members_to_chat_room
    helper. Best effort: this is realtime delivery plumbing, not the
    domain write the caller actually asked for.
    """
    room = server_room(server_id)
    for member_id in member_ids:
        try:
            await room_membership_updater.join_user_to_room(member_id, room)
        except Exception:
            logger.exception(
                "realtime.room_join_failed",
                user_id=str(member_id),
                server_id=str(server_id),
            )
