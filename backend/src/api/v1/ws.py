from typing import Annotated, cast

from fastapi import APIRouter, Depends, WebSocket

from src.core.realtime.rooms import user_room
from src.core.websocket.auth import UserIdWSDep
from src.core.websocket.manager import ConnectionManager

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


@router.websocket("/ws")
async def realtime_socket(
    websocket: WebSocket,
    user_id: UserIdWSDep,
    manager: ConnectionManagerWSDep,
) -> None:
    connection = await manager.connect(websocket, user_id)
    await manager.join_room(connection, user_room(user_id))
    await manager.serve(connection)
