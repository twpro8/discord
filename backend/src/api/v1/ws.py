import asyncio
from collections.abc import Coroutine
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, WebSocket

from src.core.realtime.envelope import Envelope, EventType
from src.core.realtime.rooms import connection_room, user_room
from src.core.websocket.auth import UserIdWSDep
from src.core.websocket.manager import ConnectionManager
from src.modules.calls.application.call_signaling_service import CallSignalingService
from src.modules.presence.application.presence_service import PresenceService

router = APIRouter()

# asyncio.create_task() only keeps a *weak* reference to the task via the
# event loop — without holding a strong reference somewhere, the task can
# be garbage-collected mid-execution (this is explicitly called out in the
# asyncio docs). Every detached offline-marking task is added here on
# creation and discarded via its own done-callback, which is what actually
# keeps it alive until it finishes.
_background_tasks: set[asyncio.Task[None]] = set()


def _fire_and_forget(coro: Coroutine[Any, Any, None]) -> None:
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


def get_connection_manager_ws(websocket: WebSocket) -> ConnectionManager:
    """Reads the singleton `ConnectionManager` off `app.state` (created in
    main.py's lifespan), via `WebSocket` since this is a WS-only need —
    unlike `get_redis`/`get_cache`/etc. in api.v1.dependencies, nothing in
    the HTTP dependency graph needs direct `ConnectionManager` access
    (chat-room membership updates go through DistributedRoomMembershipUpdater
    instead, see api/v1/dependencies.py::get_mediator)."""
    return cast(ConnectionManager, websocket.app.state.connection_manager)


ConnectionManagerWSDep = Annotated[
    ConnectionManager, Depends(get_connection_manager_ws)
]


def get_presence_service_ws(websocket: WebSocket) -> PresenceService:
    """Mirror of get_connection_manager_ws — PresenceService is likewise a
    startup singleton on app.state, not mediator-resolved (see its own
    docstring for why WS routes can't use MediatorDep)."""
    return cast(PresenceService, websocket.app.state.presence_service)


PresenceServiceDep = Annotated[PresenceService, Depends(get_presence_service_ws)]


def get_call_signaling_service_ws(websocket: WebSocket) -> CallSignalingService:
    """Mirror of get_connection_manager_ws/get_presence_service_ws —
    CallSignalingService is likewise a startup singleton on app.state, not
    mediator-resolved (see modules.calls.application.call_signaling_service
    and PresenceService's own docstring for why WS routes can't use
    MediatorDep)."""
    return cast(CallSignalingService, websocket.app.state.call_signaling_service)


CallSignalingServiceDep = Annotated[
    CallSignalingService, Depends(get_call_signaling_service_ws)
]


@router.websocket("/ws")
async def realtime_socket(
    websocket: WebSocket,
    user_id: UserIdWSDep,
    manager: ConnectionManagerWSDep,
    presence_service: PresenceServiceDep,
    call_signaling_service: CallSignalingServiceDep,
) -> None:
    connection = await manager.connect(websocket, user_id)
    await manager.join_room(connection, user_room(user_id))
    # Finest-grained delivery target — call signaling relays offer/answer/
    # ICE/accept-race-loser events to exactly this one connection via
    # connection_room, never a client-reported identifier (see plan §2.4
    # and core.realtime.rooms.connection_room's docstring).
    await manager.join_room(connection, connection_room(connection.connection_id))
    # Resyncs a call.invite that was published while this user had no open
    # connection at all (offline) and was therefore lost. Sent directly to
    # this connection (not published to a room) — see
    # CallSignalingService.get_pending_invite's docstring for why a
    # broadcast here would race the connection_room join just above.
    pending_invite = await call_signaling_service.get_pending_invite(user_id)
    if pending_invite is not None:
        await connection.send(
            Envelope(type=EventType.CALL_INVITE, payload=pending_invite)
        )
    await presence_service.mark_connection_online(user_id, connection.connection_id)
    try:
        await manager.serve(connection)
    finally:
        # serve() already calls disconnect() internally on every path
        # (clean, abrupt, or a server-shutdown cancellation propagating
        # through it) — this finally is what guarantees offline marking is
        # *scheduled* even in the cancellation case. Deliberately not
        # awaited directly: this route's own coroutine can itself be
        # cancelled here (e.g. ConnectionManager.shutdown() cancelling a
        # still-in-progress serve() call, or — found empirically — a test
        # client tearing down a WebSocket connection's task right after
        # closing it), and awaiting a DB-dependent operation at a point
        # that's still inside that cancellable scope risks it never
        # completing rather than raising cleanly. _fire_and_forget keeps a
        # strong reference so this detached task actually runs to
        # completion instead of risking GC (see its own comment) — without
        # that, this was the root cause of a real bug: a closed tab could
        # leave a user showing "online" indefinitely, not just until the
        # next sweep. If the whole process dies before it completes,
        # PresenceSweeper's periodic sweep is still the safety net for
        # that narrower case.
        _fire_and_forget(
            presence_service.mark_connection_offline(user_id, connection.connection_id)
        )
        _fire_and_forget(
            call_signaling_service.handle_disconnect(user_id, connection.connection_id)
        )
