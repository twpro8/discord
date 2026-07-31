"""Integration tests for GET /chats/{chat_id}."""

from uuid import uuid4

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


async def test_get_chat_details_as_member(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    create_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(peer.id)},
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    response = await authed_client.get(f"/api/v1/chats/{chat_id}")

    assert response.status_code == 200
    assert response.json()["id"] == chat_id


async def test_get_chat_details_not_found(authed_client: AsyncClient) -> None:
    response = await authed_client.get(f"/api/v1/chats/{uuid4()}")
    assert response.status_code == 404


async def test_get_chat_details_forbidden_for_non_member(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    others = [u for u in get_all_users if u.id != current_user.id]
    peer, outsider = others[0], others[1]

    create_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(peer.id)},
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(outsider.username), "password": "12345678"},
    )
    response = await ac.get(f"/api/v1/chats/{chat_id}")
    assert response.status_code == 403
