"""Integration tests for servers, server members, and server invites."""

from uuid import UUID, uuid4

from httpx import AsyncClient

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.value_objects.username import Username


async def _login(ac: AsyncClient, username: Username) -> None:
    response = await ac.post(
        "/api/v1/auth/login",
        json={"username": str(username), "password": "12345678"},
    )
    assert response.status_code == 200


class TestCreateServer:
    async def test_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/servers",
            json={"name": "My Server", "description": "A test server"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "My Server"
        assert data["description"] == "A test server"
        assert data["owner_id"] == str(current_user.id)
        assert data["member_count"] == 1
        assert UUID(data["id"])
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/servers",
            json={"name": "My Server"},
        )
        assert response.status_code == 401

    async def test_validation_error(self, authed_client: AsyncClient) -> None:
        response = await authed_client.post(
            "/api/v1/servers",
            json={"name": ""},
        )
        assert response.status_code == 422


class TestGetMyServers:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        await authed_client.post(
            "/api/v1/servers",
            json={"name": "My Server"},
        )
        response = await authed_client.get("/api/v1/servers")
        assert response.status_code == 200
        data = response.json()
        assert any(s["name"] == "My Server" for s in data)

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.get("/api/v1/servers")
        assert response.status_code == 401


class TestGetMyServer:
    async def test_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "My Server", "description": "desc"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.get(f"/api/v1/servers/{server_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == server_id
        assert data["name"] == "My Server"
        assert data["owner_id"] == str(current_user.id)

    async def test_not_found(self, authed_client: AsyncClient) -> None:
        response = await authed_client.get(f"/api/v1/servers/{uuid4()}")
        assert response.status_code == 404

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.get(f"/api/v1/servers/{uuid4()}")
        assert response.status_code == 401


class TestUpdateServer:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Original", "description": "Original description"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.patch(
            f"/api/v1/servers/{server_id}",
            json={"name": "Updated", "description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "Updated description"

    async def test_partial_update(self, authed_client: AsyncClient) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Original", "description": "Keep me"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.patch(
            f"/api/v1/servers/{server_id}",
            json={"name": "Only Name Changed"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Only Name Changed"
        assert data["description"] == "Keep me"

    async def test_not_found(self, authed_client: AsyncClient) -> None:
        response = await authed_client.patch(
            f"/api/v1/servers/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 404

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.patch(
            f"/api/v1/servers/{uuid4()}",
            json={"name": "Updated"},
        )
        assert response.status_code == 401

    async def test_validation_error(self, authed_client: AsyncClient) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.patch(
            f"/api/v1/servers/{server_id}",
            json={"name": ""},
        )
        assert response.status_code == 422


class TestDeleteServer:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "To Delete"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.delete(f"/api/v1/servers/{server_id}")
        assert response.status_code == 204

    async def test_not_found(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.delete(f"/api/v1/servers/{uuid4()}")
        assert response.status_code == 404

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.delete(f"/api/v1/servers/{uuid4()}")
        assert response.status_code == 401

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Johns Server"},
        )
        server_id = create_resp.json()["id"]

        monica = get_all_users[1]
        await _login(ac, monica.username)

        response = await ac.delete(f"/api/v1/servers/{server_id}")
        assert response.status_code == 404

    async def test_not_empty(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Shared Server"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        await ac.post("/api/v1/servers/join", json={"code": code})

        await _login(ac, get_all_users[0].username)

        response = await ac.delete(f"/api/v1/servers/{server_id}")
        assert response.status_code == 500


class TestTransferOwnership:
    async def test_success(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Transfer Test"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        await ac.post("/api/v1/servers/join", json={"code": code})

        await _login(ac, get_all_users[0].username)

        response = await ac.post(
            f"/api/v1/servers/{server_id}/transfer",
            json={"owner_id": str(monica.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["owner_id"] == str(monica.id)

    async def test_transfer_to_self(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Transfer Test"},
        )
        server_id = create_resp.json()["id"]

        owner_id = create_resp.json()["owner_id"]
        response = await authed_client.post(
            f"/api/v1/servers/{server_id}/transfer",
            json={"owner_id": owner_id},
        )
        assert response.status_code == 403

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Transfer Test"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        await ac.post("/api/v1/servers/join", json={"code": code})

        alice = get_all_users[2]
        response = await ac.post(
            f"/api/v1/servers/{server_id}/transfer",
            json={"owner_id": str(alice.id)},
        )
        assert response.status_code == 403

    async def test_server_not_found(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            f"/api/v1/servers/{uuid4()}/transfer",
            json={"owner_id": str(uuid4())},
        )
        assert response.status_code == 404

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.post(
            f"/api/v1/servers/{uuid4()}/transfer",
            json={"owner_id": str(uuid4())},
        )
        assert response.status_code == 401


class TestJoinServer:
    async def test_success(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Joinable Server"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        response = await ac.post(
            "/api/v1/servers/join",
            json={"code": code},
        )
        assert response.status_code == 201
        data = response.json()
        assert UUID(data["id"])
        assert data["server_id"] == server_id
        assert data["user_id"] == str(monica.id)
        assert data["role"] == "member"

    async def test_already_member(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Joinable Server"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        await ac.post("/api/v1/servers/join", json={"code": code})
        response = await ac.post(
            "/api/v1/servers/join",
            json={"code": code},
        )
        assert response.status_code == 201

    async def test_invalid_code(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/servers/join",
            json={"code": "invalidcode"},
        )
        assert response.status_code == 404

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.post(
            "/api/v1/servers/join",
            json={"code": "somecode"},
        )
        assert response.status_code == 401


class TestCreateInvite:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server With Invites"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        assert response.status_code == 201
        data = response.json()
        assert UUID(data["id"])
        assert data["server_id"] == server_id
        assert data["code"] is not None
        assert len(data["code"]) == 8
        assert data["use_count"] == 0

    async def test_with_limits(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Limited Server"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={"max_uses": 5, "expires_in": 3600},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["max_uses"] == 5
        assert data["expires_at"] is not None

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Johns Server"},
        )
        server_id = create_resp.json()["id"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        response = await ac.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        assert response.status_code == 403

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.post(
            f"/api/v1/servers/{uuid4()}/invites",
            json={},
        )
        assert response.status_code == 401


class TestGetInvites:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server With Invites"},
        )
        server_id = create_resp.json()["id"]

        await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )

        response = await authed_client.get(
            f"/api/v1/servers/{server_id}/invites",
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["code"] is not None
        assert data[0]["validity_status"] == "valid"

    async def test_empty(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server Without Invites"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.get(
            f"/api/v1/servers/{server_id}/invites",
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.get(
            f"/api/v1/servers/{uuid4()}/invites",
        )
        assert response.status_code == 401


class TestDeleteInvite:
    async def test_success(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        response = await authed_client.delete(
            f"/api/v1/servers/{server_id}/invites/{code}",
        )
        assert response.status_code == 204

    async def test_not_found(
        self,
        authed_client: AsyncClient,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Server"},
        )
        server_id = create_resp.json()["id"]

        response = await authed_client.delete(
            f"/api/v1/servers/{server_id}/invites/nonexistent",
        )
        assert response.status_code == 404

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        get_all_users: list[User],
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Johns Server"},
        )
        server_id = create_resp.json()["id"]

        invite_resp = await authed_client.post(
            f"/api/v1/servers/{server_id}/invites",
            json={},
        )
        code = invite_resp.json()["code"]

        monica = get_all_users[1]
        await _login(ac, monica.username)
        response = await ac.delete(
            f"/api/v1/servers/{server_id}/invites/{code}",
        )
        assert response.status_code == 403

    async def test_unauthorized(self, ac: AsyncClient) -> None:
        response = await ac.delete(
            f"/api/v1/servers/{uuid4()}/invites/code1234",
        )
        assert response.status_code == 401
