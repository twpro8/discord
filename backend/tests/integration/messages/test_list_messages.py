"""Integration tests for listing chat messages, including ordering,
pagination, and the auto-advance of the read cursor.

Uses group chats rather than private chats: private-chat creation is
find-or-create (design doc §3.2), so two tests using the same current_user +
peer pair would silently share one chat and its message history across the
session-scoped seeded database. Group chats are always freshly created."""

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


async def test_lists_messages_in_ascending_sequence_order(
    authed_client: AsyncClient,
) -> None:
    chat_resp = await authed_client.post(
        "/api/v1/chats", json={"type": "group", "name": "List Order Test"}
    )
    chat_id = chat_resp.json()["id"]

    for body in ("first", "second", "third"):
        send_resp = await authed_client.post(
            f"/api/v1/chats/{chat_id}/messages", json={"body": body}
        )
        assert send_resp.status_code == 200

    response = await authed_client.get(f"/api/v1/chats/{chat_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert [m["body"] for m in data["items"]] == ["first", "second", "third"]
    assert [m["sequence"] for m in data["items"]] == [1, 2, 3]
    assert data["has_more"] is False


async def test_pagination_respects_limit_and_cursor(
    authed_client: AsyncClient,
) -> None:
    chat_resp = await authed_client.post(
        "/api/v1/chats", json={"type": "group", "name": "Pagination Test"}
    )
    chat_id = chat_resp.json()["id"]

    for body in ("a", "b", "c"):
        await authed_client.post(
            f"/api/v1/chats/{chat_id}/messages", json={"body": body}
        )

    first_page = await authed_client.get(
        f"/api/v1/chats/{chat_id}/messages", params={"limit": 2}
    )
    assert first_page.status_code == 200
    first_data = first_page.json()
    assert [m["body"] for m in first_data["items"]] == ["a", "b"]
    assert first_data["has_more"] is True
    assert first_data["next_cursor"] is not None

    second_page = await authed_client.get(
        f"/api/v1/chats/{chat_id}/messages",
        params={"limit": 2, "after_cursor": first_data["next_cursor"]},
    )
    assert second_page.status_code == 200
    second_data = second_page.json()
    assert [m["body"] for m in second_data["items"]] == ["c"]
    assert second_data["has_more"] is False


async def test_listing_messages_advances_read_cursor(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)
    chat_resp = await authed_client.post(
        "/api/v1/chats",
        json={
            "type": "group",
            "name": "Read Cursor Test",
            "member_ids": [str(peer.id)],
        },
    )
    chat_id = chat_resp.json()["id"]

    await authed_client.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "hello"}
    )

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(peer.username), "password": "12345678"},
    )
    details_before = await ac.get(f"/api/v1/chats/{chat_id}")
    assert details_before.json()["unread_count"] == 1

    list_resp = await ac.get(f"/api/v1/chats/{chat_id}/messages")
    assert list_resp.status_code == 200

    details_after = await ac.get(f"/api/v1/chats/{chat_id}")
    assert details_after.json()["unread_count"] == 0
