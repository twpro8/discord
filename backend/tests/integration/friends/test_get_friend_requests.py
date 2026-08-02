from httpx import AsyncClient

from src.modules.friends.domain.enums import FriendStatus
from src.modules.users.domain.entities.user import User


async def test_get_friends_list_returns_empty_for_new_user(
    authed_client: AsyncClient,
) -> None:
    response = await authed_client.get("/api/v1/friends")

    assert response.status_code == 200
    assert response.json() == []


async def test_get_sent_friend_requests_shape(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    target = next(user for user in get_all_users if user.id != current_user.id)

    await authed_client.post(
        "/api/v1/friends/requests", json={"username": str(target.username)}
    )
    response = await authed_client.get("/api/v1/friends/requests/sent")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    entry = body[0]
    assert entry["username"] == str(target.username)
    assert set(entry.keys()) == {
        "id",
        "user_id",
        "target_user_id",
        "status",
        "created_at",
        "updated_at",
        "username",
        "avatar_url",
    }
    assert entry["status"] == FriendStatus.PENDING

    # Clean up so this doesn't collide with other tests sharing the seeded DB.
    await authed_client.delete(f"/api/v1/friends/requests/{entry['id']}")
