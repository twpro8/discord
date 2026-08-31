from typing import Annotated
from uuid import UUID

from fastapi import Depends, WebSocket
from fastapi.exceptions import WebSocketException

from src.core.security.jwt import decode_access_token
from src.modules.auth.domain.exceptions import InvalidAccessTokenError

ACCESS_TOKEN_COOKIE_NAME = "access_token"
WS_UNAUTHORIZED_CODE = 4401


async def get_access_token_ws(websocket: WebSocket) -> str:
    """WebSocket-handshake counterpart to
    `api.v1.dependencies.access_cookie_scheme`: that dependency is built on
    `fastapi.security.APIKeyCookie`, whose `__call__` takes a `Request`
    positionally and so is never resolved for `@router.websocket(...)`
    params — FastAPI injects a `WebSocket`, not a `Request`, into those.
    This reads the same cookie directly off `WebSocket.cookies` instead.
    """
    token = websocket.cookies.get(ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        raise WebSocketException(
            code=WS_UNAUTHORIZED_CODE,
            reason="Missing access token",
        )
    return token


AccessTokenWSDep = Annotated[str, Depends(get_access_token_ws)]


async def get_current_user_id_ws(access_token: AccessTokenWSDep) -> UUID:
    """WebSocket-handshake counterpart to
    `api.v1.dependencies.get_current_user_id`: same `decode_access_token`
    validation, no duplicated JWT logic — only the transport-specific
    cookie extraction (`get_access_token_ws` above) differs.

    Raising `WebSocketException` (rather than manually closing the socket)
    lets FastAPI reject the handshake with this close code before
    `websocket.accept()` is ever called, so no endpoint code runs for an
    unauthenticated client.
    """
    try:
        payload = decode_access_token(access_token)
    except InvalidAccessTokenError as error:
        raise WebSocketException(
            code=WS_UNAUTHORIZED_CODE,
            reason="Invalid access token",
        ) from error

    user_id = payload.get("sub")
    if not user_id:
        raise WebSocketException(
            code=WS_UNAUTHORIZED_CODE,
            reason="Invalid access token",
        )
    try:
        return UUID(user_id)
    except ValueError as error:
        raise WebSocketException(
            code=WS_UNAUTHORIZED_CODE,
            reason="Invalid access token",
        ) from error


UserIdWSDep = Annotated[UUID, Depends(get_current_user_id_ws)]
