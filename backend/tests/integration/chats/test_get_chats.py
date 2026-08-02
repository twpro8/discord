"""Integration tests for listing chats (exercises the discriminated
GroupChatSummary/PrivateChatSummary response union)."""

from httpx import AsyncClient

from src.modules.chats.domain.enums import ChatType
from src.modules.users.domain.entities.user import User


async def test_get_my_chats_returns_private_and_group_summaries(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    peer = next(u for u in get_all_users if u.id != current_user.id)

    private_response = await authed_client.post(
        "/api/v1/chats",
        json={"type": ChatType.private, "target_user_id": str(peer.id)},
    )
    assert private_response.status_code == 201

    group_response = await authed_client.post(
        "/api/v1/chats",
        json={"type": ChatType.group, "name": "Test Group"},
    )
    assert group_response.status_code == 201

    response = await authed_client.get("/api/v1/chats")

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"items", "next_cursor", "total"}
    assert body["total"] == 2

    items_by_type = {item["type"]: item for item in body["items"]}
    assert set(items_by_type) == {"private", "group"}

    private_item = items_by_type["private"]
    assert set(private_item.keys()) == {
        "id",
        "type",
        "peer_id",
        "peer_name",
        "peer_avatar_url",
        "unread_count",
        "last_message",
    }
    assert private_item["peer_id"] == str(peer.id)

    group_item = items_by_type["group"]
    assert set(group_item.keys()) == {
        "id",
        "type",
        "name",
        "image_url",
        "unread_count",
        "last_message",
    }
    assert group_item["name"] == "Test Group"
