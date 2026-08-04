from uuid import UUID

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.redis_pubsub import RedisSubscriptionManager
from src.core.realtime.rooms import user_room


class DistributedRoomMembershipUpdater:
    """Cross-instance RoomMembershipUpdater.

    Joining/leaving a user's connections to a room is published as a
    control-plane Envelope to `user_room(user_id)` — a channel every
    instance with a local connection for that user is already subscribed
    to, since every connection auto-joins its own user_room at connect
    time (see api/v1/ws.py). Each such instance's RedisSubscriptionManager
    receives it (`_apply_room_membership_control`) and applies the
    join/leave locally — including *this* instance's own, deliberately:
    there's no local-direct fast path here, everyone (this instance
    included) goes through the same Redis round-trip, so there's one code
    path instead of two. This is what closes the gap
    `ConnectionManager.join_user_to_room` alone can't: a user's connection
    open on a *different* instance than the one handling the write that
    grants/revokes room access now learns about it too.

    If the user has no connection open anywhere, the publish reaches zero
    subscribers and is a correct no-op — connect-time auto-join
    (`api/v1/ws.py::_resolve_active_chat_rooms`) picks up the membership
    from the DB whenever they do eventually connect.
    """

    def __init__(self, subscription_manager: RedisSubscriptionManager) -> None:
        self._subscription_manager = subscription_manager

    async def join_user_to_room(self, user_id: UUID, room: str) -> None:
        await self._publish(user_id, EventType.JOIN, room)

    async def leave_user_from_room(self, user_id: UUID, room: str) -> None:
        await self._publish(user_id, EventType.LEAVE, room)

    async def _publish(self, user_id: UUID, event_type: EventType, room: str) -> None:
        target = user_room(user_id)
        envelope = Envelope(
            type=event_type,
            payload={"user_id": str(user_id), "room": room},
            room=target,
        )
        await self._subscription_manager.publish(target, envelope)
