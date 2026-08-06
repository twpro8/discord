import uuid

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User
from tests.dependency_overrides.storage import fake_storage


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

    async def test_update_current_user_username_conflict(
        self,
        authed_client: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        other = next(u for u in get_all_users if u.id != get_all_users[0].id)
        payload = {"username": str(other.username)}
        response = await authed_client.patch("/api/v1/users/me", json=payload)
        assert response.status_code == 409  # Conflict

    async def test_update_current_user_email_conflict(
        self,
        authed_client: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        other = next(u for u in get_all_users if u.id != get_all_users[0].id)
        payload = {"email": str(other.email)}
        response = await authed_client.patch("/api/v1/users/me", json=payload)
        assert response.status_code == 409  # Conflict


class TestAvatarAPI:
    async def test_upload_avatar_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        fake_storage.objects.clear()
        response = await authed_client.put(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.png", b"fake-png-bytes", "image/png")},
        )
        assert response.status_code == 200
        data = response.json()
        key = f"user_avatar/{current_user.id}.png"
        assert key in fake_storage.objects
        assert data["avatar_url"].startswith(f"https://files.example.com/{key}?v=")

    async def test_upload_avatar_rejects_unsupported_type(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.put(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.pdf", b"%PDF", "application/pdf")},
        )
        assert response.status_code == 415

    async def test_upload_avatar_requires_auth(self, ac: AsyncClient) -> None:
        response = await ac.put(
            "/api/v1/users/me/avatar",
            files={"file": ("avatar.png", b"bytes", "image/png")},
        )
        assert response.status_code == 401


class TestPasswordAPI:
    async def test_change_password_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        # Restore the seeded password afterwards: the integration DB is
        # only reset once per session and `authed_client` logs in with it.
        try:
            response = await authed_client.post(
                "/api/v1/users/me/password",
                json={
                    "current_password": "12345678",
                    "new_password": "newpassword123",
                },
            )
            assert response.status_code == 204

            response = await authed_client.post(
                "/api/v1/users/me/password",
                json={
                    "current_password": "newpassword123",
                    "new_password": "12345678",
                },
            )
            assert response.status_code == 204
        finally:
            await authed_client.post(
                "/api/v1/users/me/password",
                json={
                    "current_password": "newpassword123",
                    "new_password": "12345678",
                },
            )

    async def test_change_password_wrong_current(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 401

    async def test_change_password_validation_error(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "12345678",
                "new_password": "ab",
            },
        )
        assert response.status_code == 422

    async def test_change_password_requires_auth(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/users/me/password",
            json={
                "current_password": "12345678",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 401
