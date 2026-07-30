import uuid

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


class TestUsersAPI:
    async def test_get_current_user_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        response = await authed_client.get("/api/v1/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(current_user.id)
        assert data["username"] == str(current_user.username)
        assert data["email"] == str(current_user.email)
        assert "password_hash" not in data

    async def test_get_current_user_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_get_user_by_id_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        response = await authed_client.get(f"/api/v1/users/{current_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(current_user.id)
        assert data["username"] == str(current_user.username)

    async def test_get_user_by_id_not_found(self, authed_client: AsyncClient) -> None:
        random_id = uuid.uuid4()
        response = await authed_client.get(f"/api/v1/users/{random_id}")
        assert response.status_code == 404

    async def test_update_current_user_success(
        self, authed_client: AsyncClient
    ) -> None:
        payload = {"name": "New Updated Name"}
        response = await authed_client.patch("/api/v1/users/me", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Updated Name"

    async def test_update_current_user_validation_error(
        self,
        authed_client: AsyncClient,
    ) -> None:
        payload = {"username": "ab"}
        response = await authed_client.patch("/api/v1/users/me", json=payload)
        assert response.status_code == 422  # Validation Error
