"""Integration tests for authentication."""

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User


class TestRegister:
    async def test_success(
        self,
        ac: AsyncClient,
    ) -> None:
        response = await ac.post(
            "/api/v1/auth/register",
            json={
                "name": "Test User",
                "username": "testuser",
                "email": "testuser@test.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert data["username"] == "testuser"
        assert data["email"] == "testuser@test.com"
        assert data["is_active"] is True
        assert data["id"] is not None
        assert "password" not in data
        assert "password_hash" not in data
        assert response.headers["location"].endswith(
            f"/api/v1/auth/register/{data['id']}"
        )

    async def test_validation_error(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/auth/register",
            json={"name": "", "username": "", "email": "invalid", "password": ""},
        )
        assert response.status_code == 422


class TestLogin:
    async def test_success(
        self,
        ac: AsyncClient,
        current_user: User,
    ) -> None:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"username": current_user.username, "password": "12345678"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}
        assert ac.cookies.get("access_token")
        assert ac.cookies.get("refresh_token")

    async def test_incorrect_password(
        self,
        ac: AsyncClient,
        current_user: User,
    ) -> None:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"username": current_user.username, "password": "wrongpass"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect password"

    async def test_user_not_found(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "12345678"},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    async def test_validation_error(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/auth/login",
            json={"username": "", "password": ""},
        )
        assert response.status_code == 422


class TestRefresh:
    async def test_success(
        self,
        ac: AsyncClient,
        current_user: User,
    ) -> None:
        await ac.post(
            "/api/v1/auth/login",
            json={"username": current_user.username, "password": "12345678"},
        )
        response = await ac.post("/api/v1/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"status": "OK"}
        assert ac.cookies.get("access_token")
        assert ac.cookies.get("refresh_token")

    async def test_missing_token(self, ac: AsyncClient) -> None:
        response = await ac.post("/api/v1/auth/refresh")
        assert response.status_code == 401
        assert response.json()["detail"] == "Authorization error"

    async def test_invalid_token(self, ac: AsyncClient) -> None:
        ac.cookies.set("refresh_token", "invalidtoken")
        response = await ac.post("/api/v1/auth/refresh")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"


class TestLogout:
    async def test_success(
        self,
        ac: AsyncClient,
        current_user: User,
    ) -> None:
        await ac.post(
            "/api/v1/auth/login",
            json={"username": current_user.username, "password": "12345678"},
        )
        assert ac.cookies.get("refresh_token")

        response = await ac.post("/api/v1/auth/logout")
        assert response.status_code == 204
        assert ac.cookies.get("access_token") is None or "Max-Age=0" in str(
            response.headers.get("set-cookie", "")
        )

    async def test_without_token(self, ac: AsyncClient) -> None:
        response = await ac.post("/api/v1/auth/logout")
        assert response.status_code == 204

    async def test_invalid_token(self, ac: AsyncClient) -> None:
        ac.cookies.set("refresh_token", "invalidtoken")
        response = await ac.post("/api/v1/auth/logout")
        assert response.status_code == 204
