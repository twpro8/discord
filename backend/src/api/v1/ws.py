from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.database.session import get_session_factory
from src.core.realtime.rooms import chat_room, user_room
from src.core.websocket.auth import UserIdWSDep
from src.core.websocket.manager import ConnectionManager
from src.modules.chats.public.facade import build_chats_facade

router = APIRouter()


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


def get_session_factory_ws() -> async_sessionmaker[AsyncSession]:
    """A dependency wrapper around the (lru_cache'd) session factory
    purely so it's overridable via `app.dependency_overrides` in tests
    (e.g. swapped for the NullPool-based test factory, same reason
    `api.v1.dependencies.get_session` is overridden there) — calling
    `get_session_factory()` directly would silently keep using the
    production, connection-pooled engine even under a test override.
    """
    return get_session_factory()


SessionFactoryWSDep = Annotated[
    async_sessionmaker[AsyncSession], Depends(get_session_factory_ws)
]


async def _resolve_active_chat_rooms(
    user_id: UUID, session_factory: async_sessionmaker[AsyncSession]
) -> set[str]:
    """One-off session, scoped to this single connect-time read — not a
    `Depends(get_session)`, which would hold a session open for the
    WebSocket's entire (potentially hours-long) lifetime for no reason.
    """
    async with session_factory() as session:
        chats_facade = build_chats_facade(session)
        chat_ids = await chats_facade.list_active_chat_ids(user_id)
    return {chat_room(chat_id) for chat_id in chat_ids}


@router.websocket("/ws")
async def realtime_socket(
    websocket: WebSocket,
    user_id: UserIdWSDep,
    manager: ConnectionManagerWSDep,
    session_factory: SessionFactoryWSDep,
) -> None:
    # Resolved *before* connect() registers anything with the manager: if
    # a disconnect/shutdown races this DB read, there's nothing yet for
    # ConnectionManager to force-cancel mid-query (cancelling a
    # SQLAlchemy/asyncpg greenlet-bridged call mid-flight is a known
    # source of hangs, not something to let a race trigger).
    rooms = await _resolve_active_chat_rooms(user_id, session_factory)

    connection = await manager.connect(websocket, user_id)
    # Permanent pseudo-room every connection gets, regardless of any
    # chat/channel room concept — the floor for delivery to this user
    # (see plan §3.3), and also the channel DistributedRoomMembershipUpdater
    # uses to reach this connection dynamically after a chat/membership
    # change (see core.realtime.membership).
    await manager.join_room(connection, user_room(user_id))
    for room in rooms:
        await manager.join_room(connection, room)
    # Must be awaited directly, not spawned as a background task: this
    # handler's own coroutine is the connection's ASGI lifetime (see
    # ConnectionManager.serve's docstring).
    await manager.serve(connection)
