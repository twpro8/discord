import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, cast
from uuid import UUID

from starlette.websockets import WebSocketDisconnect

from src.core.logging import get_logger
from src.core.realtime.envelope import Envelope
from src.core.websocket.connection import Connection, SendableWebSocket

logger = get_logger(__name__)


class ManagedWebSocket(SendableWebSocket, Protocol):
    """What ConnectionManager needs beyond Connection's narrower send-only
    view: the handshake accept and the read side, for the reader loop this
    class owns (see module docstring on `_read_loop`)."""

    async def accept(self) -> None: ...

    async def receive_text(self) -> str: ...


ActivityCallback = Callable[[UUID, UUID, str], Awaitable[None]]
"""Invoked on every inbound frame from `serve()`'s reader loop, with
(user_id, connection_id, raw_text) — the raw frame text so a listener
(presence's heartbeat handling) can parse it without this layer knowing
anything about that format. Kept optional/pluggable rather than a fixed
dependency so `core/websocket` stays free of any module-specific import,
same rationale as RoomTransitionCallback below."""

RoomTransitionCallback = Callable[[str], Awaitable[None]]
"""Invoked when a room's local subscriber count transitions 0->1
(`on_room_activated`) or 1->0 (`on_room_deactivated`). Unused by this
local-only manager; PR6 wires these to hand subscribe/unsubscribe
requests to the single Redis listener task. Deliberately not guarded by
a lock here: the local index mutation that decides whether a transition
happened completes synchronously (no `await` in between), so two
concurrent join_room/leave_room calls can't both observe a stale
pre-mutation state — the ordering guarantee PR6 needs (e.g. a leave's
unsubscribe not racing an immediately-following join's subscribe for the
same room) instead comes from those callbacks being invoked in the same
order the transitions actually happened, which a FIFO request queue to
one owning task (§3.6 of the plan) preserves; a manager-level lock would
be redundant with that."""


class RoomMembershipUpdater(Protocol):
    """Narrow capability for modules that need to update a user's live
    connection room-membership as a side effect of a domain write — e.g.
    joining a newly-added chat member's open socket to the chat's room —
    without needing the rest of ConnectionManager's surface (connect,
    serve, broadcast, ...). `ConnectionManager` satisfies this
    structurally.
    """

    async def join_user_to_room(self, user_id: UUID, room: str) -> None: ...

    async def leave_user_from_room(self, user_id: UUID, room: str) -> None: ...


class ConnectionManager:
    """Owns all active local WebSocket Connections for this process.

    Cross-instance fan-out is out of scope here — see core.realtime for
    the Redis layer that extends delivery across processes. This class
    only knows about connections on this instance.
    """

    def __init__(
        self,
        *,
        queue_maxsize: int = 256,
        on_room_activated: RoomTransitionCallback | None = None,
        on_room_deactivated: RoomTransitionCallback | None = None,
        on_activity: ActivityCallback | None = None,
    ) -> None:
        self._queue_maxsize = queue_maxsize
        self._on_room_activated = on_room_activated
        self._on_room_deactivated = on_room_deactivated
        self._on_activity = on_activity
        self._connections: dict[UUID, Connection] = {}
        self._rooms: dict[str, set[UUID]] = {}
        self._user_connections: dict[UUID, set[UUID]] = {}
        self._serving_tasks: dict[UUID, asyncio.Task[None]] = {}

    def set_room_transition_callbacks(
        self,
        *,
        on_room_activated: RoomTransitionCallback | None,
        on_room_deactivated: RoomTransitionCallback | None,
    ) -> None:
        """Escape hatch for the construction-order puzzle where the
        callback owner (e.g. RedisSubscriptionManager) itself needs this
        ConnectionManager instance to already exist — bind after both are
        constructed rather than requiring one to exist before the other.
        Only meaningful before any room activity happens; not meant as a
        way to swap callbacks on a live manager.
        """
        self._on_room_activated = on_room_activated
        self._on_room_deactivated = on_room_deactivated

    def set_activity_callback(self, on_activity: ActivityCallback | None) -> None:
        """Mirror of `set_room_transition_callbacks` — same construction-order
        rationale (the callback owner needs this ConnectionManager instance
        to already exist)."""
        self._on_activity = on_activity

    async def connect(
        self,
        websocket: ManagedWebSocket,
        user_id: UUID,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> Connection:
        """Accept the handshake and register the connection. Does **not**
        start reading — call `serve()` right after, awaited directly by
        the caller. See `serve()` for why.
        """
        await websocket.accept()
        connection = Connection(
            websocket,
            user_id,
            queue_maxsize=self._queue_maxsize,
            on_disconnect_needed=self.disconnect,
        )
        if metadata:
            connection.metadata.update(metadata)

        self._connections[connection.connection_id] = connection
        self._user_connections.setdefault(user_id, set()).add(connection.connection_id)
        logger.info(
            "websocket.connected",
            connection_id=str(connection.connection_id),
            user_id=str(user_id),
        )
        return connection

    async def disconnect(
        self, connection: Connection, *, already_disconnected: bool = False
    ) -> None:
        """`already_disconnected=True` means the transport is already
        known gone (a clean client-initiated disconnect — see `serve()`)
        — passed straight through to `Connection.close()` so it doesn't
        attempt (and fail) a redundant socket close. Defaults to False
        for every other path (overflow, write failure, server shutdown),
        where the socket may still be alive and does need an active
        close.
        """
        if connection.connection_id not in self._connections:
            return
        del self._connections[connection.connection_id]

        user_connections = self._user_connections.get(connection.user_id)
        if user_connections is not None:
            user_connections.discard(connection.connection_id)
            if not user_connections:
                del self._user_connections[connection.user_id]

        for room in list(connection.rooms):
            await self.leave_room(connection, room)

        serving_task = self._serving_tasks.pop(connection.connection_id, None)
        if serving_task is not None and serving_task is not asyncio.current_task():
            serving_task.cancel()

        await connection.close(already_disconnected=already_disconnected)
        logger.info(
            "websocket.disconnected",
            connection_id=str(connection.connection_id),
            user_id=str(connection.user_id),
        )

    async def join_room(self, connection: Connection, room: str) -> None:
        if connection.connection_id not in self._connections:
            return
        members = self._rooms.setdefault(room, set())
        newly_activated = not members
        members.add(connection.connection_id)
        connection.rooms.add(room)
        if newly_activated and self._on_room_activated is not None:
            await self._on_room_activated(room)

    async def leave_room(self, connection: Connection, room: str) -> None:
        members = self._rooms.get(room)
        connection.rooms.discard(room)
        if members is None:
            return
        members.discard(connection.connection_id)
        if not members:
            del self._rooms[room]
            if self._on_room_deactivated is not None:
                await self._on_room_deactivated(room)

    async def join_user_to_room(self, user_id: UUID, room: str) -> None:
        """Join every one of this user's currently-open *local*
        connections (there can be more than one — multiple devices/tabs)
        to `room`. Deliberately local-instance only, as a building block:
        a connection open on a different instance isn't reached from
        here. Cross-instance reach is a separate concern layered on top —
        see `core.realtime.membership.DistributedRoomMembershipUpdater`,
        which every instance's `RedisSubscriptionManager` calls back into
        via this same method for a signal that originated elsewhere.
        """
        for connection_id in list(self._user_connections.get(user_id, set())):
            connection = self._connections.get(connection_id)
            if connection is not None:
                await self.join_room(connection, room)

    async def leave_user_from_room(self, user_id: UUID, room: str) -> None:
        """Mirror of `join_user_to_room` — see its docstring."""
        for connection_id in list(self._user_connections.get(user_id, set())):
            connection = self._connections.get(connection_id)
            if connection is not None:
                await self.leave_room(connection, room)

    async def broadcast_to_room(self, room: str, envelope: Envelope) -> None:
        """Local delivery only — connections on this instance currently
        joined to `room`. Cross-instance fan-out is the Redis layer's job
        (core.realtime), which calls back into this method for messages
        that originated elsewhere."""
        connection_ids = self._rooms.get(room)
        if not connection_ids:
            return
        for connection_id in list(connection_ids):
            connection = self._connections.get(connection_id)
            if connection is not None:
                await connection.send(envelope)

    async def shutdown(self) -> None:
        """Disconnect every locally-held connection, e.g. on app shutdown."""
        for connection in list(self._connections.values()):
            await self.disconnect(connection)

    async def serve(self, connection: Connection) -> None:
        """Run the reader loop for this connection until it disconnects.

        Owned here, not by Connection, so Connection stays a pure
        send-side primitive with no knowledge of room membership or
        manager-level indices — but that means whoever accepted this
        connection (a `@router.websocket(...)` handler) must `await` this
        directly, not fire it off as a background task: a FastAPI/Starlette
        WebSocket route's own coroutine *is* the connection's ASGI
        lifetime, so returning from the handler right after `connect()`
        would let Starlette tear the connection down independently of
        this manager's bookkeeping, regardless of what a detached reader
        task thinks is still open.
        """
        self._serving_tasks[connection.connection_id] = cast(
            "asyncio.Task[None]", asyncio.current_task()
        )
        websocket = cast(ManagedWebSocket, connection.websocket)
        client_disconnected = False
        try:
            while True:
                raw_text = await websocket.receive_text()
                connection.touch()
                if self._on_activity is not None:
                    await self._on_activity(
                        connection.user_id, connection.connection_id, raw_text
                    )
        except WebSocketDisconnect:
            client_disconnected = True
            logger.info(
                "websocket.client_disconnected",
                connection_id=str(connection.connection_id),
            )
        except Exception:
            logger.exception(
                "websocket.read_failed",
                connection_id=str(connection.connection_id),
            )
        finally:
            await self.disconnect(connection, already_disconnected=client_disconnected)
