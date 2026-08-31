"""Proves the WS-native auth dependency rejects the handshake *before*
`websocket.accept()` runs, using a small standalone app rather than
`src.main.app` — this is pure FastAPI/Depends() mechanics, independent of
whatever `api/v1/ws.py` evolves into."""

from uuid import uuid4

import pytest
from fastapi import FastAPI, WebSocket
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.core.security.jwt import create_access_token
from src.core.realtime.auth import UserIdWSDep


def _build_test_app() -> FastAPI:
    app = FastAPI()

    @app.websocket("/testws")
    async def websocket_endpoint(websocket: WebSocket, user_id: UserIdWSDep) -> None:
        await websocket.accept()
        await websocket.send_json({"user_id": str(user_id)})

    return app


def test_missing_cookie_rejects_before_accept() -> None:
    client = TestClient(_build_test_app())

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/testws"):
            pass

    assert exc_info.value.code == 4401


def test_invalid_token_rejects_before_accept() -> None:
    client = TestClient(_build_test_app())
    client.cookies.set("access_token", "not-a-real-jwt")

    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/testws"):
            pass

    assert exc_info.value.code == 4401


def test_valid_token_accepts_and_resolves_user_id() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)
    client = TestClient(_build_test_app())
    client.cookies.set("access_token", token)

    with client.websocket_connect("/testws") as websocket:
        message = websocket.receive_json()

    assert message["user_id"] == str(user_id)
