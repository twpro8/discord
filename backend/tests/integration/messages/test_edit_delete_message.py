"""Integration tests for editing and deleting chat messages."""

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


async def test_sender_can_edit_own_message(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    chat_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(peer.id)},
    )
    chat_id = chat_resp.json()["id"]

    send_resp = await authed_client.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "original"}
    )
    assert send_resp.status_code == 200
    message_id = send_resp.json()["id"]

    edit_resp = await authed_client.patch(
        f"/api/v1/chats/{chat_id}/messages/{message_id}", json={"body": "edited"}
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["body"] == "edited"
    assert edit_resp.json()["is_edited"] is True


async def test_non_sender_cannot_edit_message(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    chat_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(peer.id)},
    )
    chat_id = chat_resp.json()["id"]

    send_resp = await authed_client.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "original"}
    )
    message_id = send_resp.json()["id"]

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(peer.username), "password": "12345678"},
    )
    response = await ac.patch(
        f"/api/v1/chats/{chat_id}/messages/{message_id}", json={"body": "hacked"}
    )
    assert response.status_code == 403


async def test_sender_can_delete_own_message(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    chat_resp = await authed_client.post(
        "/api/v1/chats",
        json={"type": "private", "target_user_id": str(peer.id)},
    )
    chat_id = chat_resp.json()["id"]

    send_resp = await authed_client.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "to delete"}
    )
    message_id = send_resp.json()["id"]

    delete_resp = await authed_client.delete(
        f"/api/v1/chats/{chat_id}/messages/{message_id}"
    )
    assert delete_resp.status_code == 204


async def test_group_owner_can_delete_others_message(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    member = next(u for u in get_all_users if u.id != current_user.id)
    chat_resp = await authed_client.post(
        "/api/v1/chats",
        json={
            "type": "group",
            "name": "Delete Test",
            "member_ids": [str(member.id)],
        },
    )
    chat_id = chat_resp.json()["id"]

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(member.username), "password": "12345678"},
    )
    send_resp = await ac.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "member message"}
    )
    message_id = send_resp.json()["id"]

    delete_resp = await authed_client.delete(
        f"/api/v1/chats/{chat_id}/messages/{message_id}"
    )
    assert delete_resp.status_code == 204
