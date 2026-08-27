import asyncio
from collections.abc import Coroutine
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, WebSocket

from src.core.realtime.rooms import user_room
from src.core.websocket.auth import UserIdWSDep
from src.core.websocket.manager import ConnectionManager
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
    instead, see api/v1/dependencies.py::get_room_membership_updater)."""
    return cast(ConnectionManager, websocket.app.state.connection_manager)


ConnectionManagerWSDep = Annotated[
    ConnectionManager, Depends(get_connection_manager_ws)
]


def get_presence_service_ws(websocket: WebSocket) -> PresenceService:
    """Mirror of get_connection_manager_ws — PresenceService is likewise a
    startup singleton on app.state, not use-case-resolved (see its own
    docstring for why WS routes can't use per-request `Depends()`)."""
    return cast(PresenceService, websocket.app.state.presence_service)


PresenceServiceDep = Annotated[PresenceService, Depends(get_presence_service_ws)]


@router.websocket("/ws")
async def realtime_socket(
    websocket: WebSocket,
    user_id: UserIdWSDep,
    manager: ConnectionManagerWSDep,
    presence_service: PresenceServiceDep,
) -> None:
    connection = await manager.connect(websocket, user_id)
    await manager.join_room(connection, user_room(user_id))
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
