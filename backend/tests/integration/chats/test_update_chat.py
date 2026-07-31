"""Integration tests for PATCH /chats/{chat_id}."""

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


async def test_owner_can_rename_group_chat(authed_client: AsyncClient) -> None:
    create_resp = await authed_client.post(
        "/api/v1/chats", json={"type": "group", "name": "Old Name"}
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    response = await authed_client.patch(
        f"/api/v1/chats/{chat_id}", json={"name": "New Name"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


async def test_non_owner_cannot_rename_group_chat(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    create_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "group", "name": "Old Name", "member_ids": [str(peer.id)]},
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(peer.username), "password": "12345678"},
    )
    response = await ac.patch(f"/api/v1/chats/{chat_id}", json={"name": "New Name"})
    assert response.status_code == 403


async def test_cannot_rename_private_chat(
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

    response = await authed_client.patch(
        f"/api/v1/chats/{chat_id}", json={"name": "New Name"}
    )
    assert response.status_code == 403
