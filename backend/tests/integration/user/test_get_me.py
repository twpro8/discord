from httpx import AsyncClient

from src.modules.users.domain.schemas import User


async def test_get_me(authed_client: AsyncClient, current_user: User) -> None:
    response = await authed_client.get("/api/v1/users/me")
    assert response.status_code == 200

    user = response.json()
    _current_user = current_user.model_dump(mode="json")

    assert user.get("id") == _current_user["id"]
    assert user.get("name") == _current_user["name"]
    assert user.get("username") == _current_user["username"]
    assert user.get("email") == _current_user["email"]
    assert user.get("avatar_url") == _current_user["avatar_url"]
    assert user.get("is_active") == _current_user["is_active"]
    assert user.get("created_at") == _current_user["created_at"]
    assert user.get("updated_at") == _current_user["updated_at"]
