from httpx import AsyncClient

from src.modules.chats.domain.enums import ChatType
from src.modules.users.domain.entities.user import User


async def test_create_private_chat_valid(
    authed_client: AsyncClient,
    current_user: User,
    get_all_users: list[User],
) -> None:
    user = next((u for u in get_all_users if current_user.id != u.id), None)
    assert user is not None
    data = {
        "type": ChatType.private,
        "target_user_id": str(user.id),
    }
    response = await authed_client.post("/api/v1/chats", json=data)
    assert response.status_code == 201

    response_json = response.json()

    assert response_json["type"] == data["type"]
    assert response_json["peer_id"] == data["target_user_id"]
    assert "id" in response_json
    assert response_json["unread_count"] == 0
    assert response_json["last_message"] is None


async def test_create_chat_unauthorized(
    ac: AsyncClient,
    get_all_users: list[User],
) -> None:
    user_id = str(get_all_users[1].id)
    data = {
        "type": ChatType.private,
        "target_user_id": user_id,
    }
    response = await ac.post("/api/v1/chats", json=data)
    assert response.status_code == 401


async def test_create_private_chat_invalid(
    authed_client: AsyncClient,
    current_user: User,
) -> None:
    data = {
        "type": ChatType.private,
        "target_user_id": str(current_user.id),
    }
    response = await authed_client.post("/api/v1/chats", json=data)
    assert response.status_code == 400
