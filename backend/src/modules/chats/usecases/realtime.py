from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.manager import RoomMembershipUpdater
from src.core.realtime.rooms import chat_room

logger = get_logger(__name__)


async def join_members_to_chat_room(
    room_membership_updater: RoomMembershipUpdater,
    chat_id: UUID,
    member_ids: list[UUID],
) -> None:
    """Join each member's already-open connections (if any) to the chat's
    room, so a connection that predates the chat's/membership's existence
    still gets joined — without this, a connection that connected before
    the chat existed would never learn the room exists (see
    core.realtime.rooms.chat_room's docstring). Best effort: this is
    realtime delivery plumbing, not the domain write the caller actually
    asked for.
    """
    room = chat_room(chat_id)
    for member_id in member_ids:
        try:
            await room_membership_updater.join_user_to_room(member_id, room)
        except Exception:
            logger.exception(
                "realtime.room_join_failed",
                user_id=str(member_id),
                chat_id=str(chat_id),
            )


async def leave_members_from_chat_room(
    room_membership_updater: RoomMembershipUpdater,
    chat_id: UUID,
    member_ids: list[UUID],
) -> None:
    """Mirror of `join_members_to_chat_room` for members leaving/removed
    — without this, a removed member's still-open connection would keep
    receiving the chat's messages until they reconnect."""
    room = chat_room(chat_id)
    for member_id in member_ids:
        try:
            await room_membership_updater.leave_user_from_room(member_id, room)
        except Exception:
            logger.exception(
                "realtime.room_leave_failed",
                user_id=str(member_id),
                chat_id=str(chat_id),
            )
