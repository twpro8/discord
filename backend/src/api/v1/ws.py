from typing import cast
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from src.core.logging import get_logger
from src.core.realtime.notifier import user_topic
from src.core.realtime.redis_pubsub import RedisPubSubTransport
from src.core.security.jwt import decode_access_token
from src.modules.auth.domain.exceptions import InvalidAccessTokenError

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def realtime_socket(websocket: WebSocket) -> None:
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=4401)
        return

    try:
        user_id = UUID(decode_access_token(token)["sub"])
    except (InvalidAccessTokenError, ValueError):
        await websocket.close(code=4401)
        return

    await websocket.accept()
    logger.info(
        "websocket.connected",
        user_id=str(user_id),
    )

    # Resolve the pub/sub transport from the app state directly: FastAPI
    # injects a Request, not a WebSocket, into regular (HTTP) dependencies,
    # so the shared `get_pubsub` dependency cannot be reused here.
    pubsub = RedisPubSubTransport(cast(Redis, websocket.app.state.redis))
    try:
        async for payload in pubsub.subscribe(user_topic(user_id)):
            await websocket.send_text(payload)
    except WebSocketDisconnect:
        logger.info("websocket.disconnected", user_id=str(user_id))
