"""Integration tests for chat member management and read-cursor endpoints."""

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


async def test_list_add_remove_members(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    others = [u for u in get_all_users if u.id != current_user.id]
    member, to_add = others[0], others[1]

    create_resp = await authed_client.post(
        "/api/v1/chats",
        json={
            "type": "group",
            "name": "Members Test",
            "member_ids": [str(member.id)],
        },
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    list_resp = await authed_client.get(f"/api/v1/chats/{chat_id}/members")
    assert list_resp.status_code == 200
    assert {m["user_id"] for m in list_resp.json()} == {
        str(current_user.id),
        str(member.id),
    }

    add_resp = await authed_client.post(
        f"/api/v1/chats/{chat_id}/members",
        json={"user_ids": [str(to_add.id), str(member.id)]},
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["added"] == [str(to_add.id)]
    assert add_resp.json()["skipped"] == [str(member.id)]

    remove_resp = await authed_client.delete(
        f"/api/v1/chats/{chat_id}/members/{to_add.id}"
    )
    assert remove_resp.status_code == 204

    list_resp = await authed_client.get(f"/api/v1/chats/{chat_id}/members")
    assert {m["user_id"] for m in list_resp.json()} == {
        str(current_user.id),
        str(member.id),
    }


async def test_owner_leaving_transfers_ownership(
    ac: AsyncClient,
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    others = [u for u in get_all_users if u.id != current_user.id]
    member = others[0]

    create_resp = await authed_client.post(
        "/api/v1/chats",
        json={
            "type": "group",
            "name": "Ownership Test",
            "member_ids": [str(member.id)],
        },
    )
    assert create_resp.status_code == 201
    chat_id = create_resp.json()["id"]

    leave_resp = await authed_client.post(f"/api/v1/chats/{chat_id}/leave")
    assert leave_resp.status_code == 204

    await ac.post(
        "/api/v1/auth/login",
        json={"username": str(member.username), "password": "12345678"},
    )
    # Ownership transferred to the remaining member — proven behaviorally,
    # since GroupChatSummaryResponse doesn't expose owner_id: only the owner
    # can rename a group chat.
    rename_resp = await ac.patch(
        f"/api/v1/chats/{chat_id}", json={"name": "Renamed by new owner"}
    )
    assert rename_resp.status_code == 200
    assert rename_resp.json()["name"] == "Renamed by new owner"


async def test_mark_chat_as_read(
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

    await authed_client.post(
        f"/api/v1/chats/{chat_id}/messages", json={"body": "hello"}
    )

    response = await authed_client.post(f"/api/v1/chats/{chat_id}/read")
    assert response.status_code == 204
