"""Integration tests for the Prometheus metrics endpoint."""

from httpx import AsyncClient


class TestMetrics:
    async def test_success(self, ac: AsyncClient) -> None:
        # Guarantee at least one instrumented request happened this
        # session, independent of test execution order.
        await ac.get("/api/v1/health")

        response = await ac.get("/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
