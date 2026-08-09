"""Integration tests for messages."""

from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.modules.users.domain.entities.user import User


class TestSendChannelMessage:
    async def test_success(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Msg Server"},
        )
        assert create_resp.status_code == 201

        result = await session.execute(select(ChannelOrm).limit(1))
        channel = result.scalar_one()

        response = await authed_client.post(
            f"/api/v1/channels/{channel.id}/messages",
            json={"body": "Hello from channel!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Hello from channel!"
        assert data["channel_id"] == str(channel.id)
        assert data["sequence"] == 1
        assert UUID(data["sender_id"])
        assert data["parent_id"] is None
        assert data["is_edited"] is False
        assert data["is_deleted"] is False

    async def test_unauthorized(
        self,
        ac: AsyncClient,
    ) -> None:
        response = await ac.post(
            "/api/v1/channels/00000000-0000-0000-0000-000000000000/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 401

    async def test_validation_error(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        result = await session.execute(select(ChannelOrm).limit(1))
        channel = result.scalar_one()

        response = await authed_client.post(
            f"/api/v1/channels/{channel.id}/messages",
            json={"body": ""},
        )
        assert response.status_code == 422

    async def test_channel_not_found(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/channels/00000000-0000-0000-0000-000000000000/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 404

    async def test_not_member(
        self,
        ac: AsyncClient,
        authed_client: AsyncClient,
        get_all_users: list[User],
        session: AsyncSession,
    ) -> None:
        create_resp = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Not Member Server"},
        )
        assert create_resp.status_code == 201

        result = await session.execute(
            select(ChannelOrm).order_by(ChannelOrm.created_at.desc()).limit(1)
        )
        channel = result.scalar_one()

        alice = next(u for u in get_all_users if str(u.username) == "alice")
        await ac.post(
            "/api/v1/auth/login",
            json={"username": str(alice.username), "password": "12345678"},
        )
        response = await ac.post(
            f"/api/v1/channels/{channel.id}/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 403


class TestSendChatMessage:
    async def test_success(
        self,
        authed_client: AsyncClient,
        current_user: User,
        get_all_users: list[User],
    ) -> None:
        other = next(u for u in get_all_users if u.id != current_user.id)

        chat_resp = await authed_client.post(
            "/api/v1/chats",
            json={
                "type": "private",
                "target_user_id": str(other.id),
            },
        )
        assert chat_resp.status_code == 201
        # Private-chat creation is find-or-create (design doc §3.2), so a
        # session-scoped seeded database shared with other tests may
        # already have a chat for this pair — use the id the create call
        # itself returns rather than guessing via a DB query (which, with
        # no reliable ordering, can't tell "this pair's chat" apart from
        # any other chat created earlier in the session).
        chat_id = chat_resp.json()["id"]

        response = await authed_client.post(
            f"/api/v1/chats/{chat_id}/messages",
            json={"body": "Hello from chat!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["body"] == "Hello from chat!"
        assert data["chat_id"] == chat_id
        assert data["sequence"] == 1
        assert UUID(data["sender_id"])
        assert data["parent_id"] is None
        assert data["is_edited"] is False
        assert data["is_deleted"] is False

    async def test_unauthorized(
        self,
        ac: AsyncClient,
    ) -> None:
        response = await ac.post(
            "/api/v1/chats/00000000-0000-0000-0000-000000000000/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 401

    async def test_validation_error(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/chats/00000000-0000-0000-0000-000000000000/messages",
            json={"body": ""},
        )
        assert response.status_code == 422

    async def test_chat_not_found(
        self,
        authed_client: AsyncClient,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/chats/00000000-0000-0000-0000-000000000000/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 404

    async def test_not_member(
        self,
        ac: AsyncClient,
        authed_client: AsyncClient,
        current_user: User,
        get_all_users: list[User],
    ) -> None:
        other = next(u for u in get_all_users if u.id != current_user.id)

        chat_resp = await authed_client.post(
            "/api/v1/chats",
            json={
                "type": "private",
                "target_user_id": str(other.id),
            },
        )
        assert chat_resp.status_code == 201
        # See test_success's comment: use the id directly rather than
        # guessing via an unordered/best-effort DB query.
        chat_id = chat_resp.json()["id"]

        alice = next(u for u in get_all_users if str(u.username) == "alice")
        await ac.post(
            "/api/v1/auth/login",
            json={"username": str(alice.username), "password": "12345678"},
        )
        response = await ac.post(
            f"/api/v1/chats/{chat_id}/messages",
            json={"body": "hello"},
        )
        assert response.status_code == 403

    async def test_sequence_increments_monotonically(
        self,
        authed_client: AsyncClient,
    ) -> None:
        # A group chat, not a private chat: private-chat creation is
        # find-or-create (design doc §3.2), so reusing the same
        # current_user + peer pair across tests in this session-scoped
        # database would share message history with other tests.
        chat_resp = await authed_client.post(
            "/api/v1/chats",
            json={"type": "group", "name": "Sequence Test"},
        )
        assert chat_resp.status_code == 201
        chat_id = chat_resp.json()["id"]

        sequences = []
        for body in ("one", "two", "three"):
            response = await authed_client.post(
                f"/api/v1/chats/{chat_id}/messages",
                json={"body": body},
            )
            assert response.status_code == 200
            sequences.append(response.json()["sequence"])

        assert sequences == [1, 2, 3]
