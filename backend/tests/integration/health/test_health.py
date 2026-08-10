"""Integration tests for the health-check endpoint."""

from httpx import AsyncClient

from src.core.version import get_app_version


class TestHealthCheck:
    async def test_success(self, ac: AsyncClient) -> None:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": get_app_version()}
