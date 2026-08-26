"""Integration tests for channels.

The only currently-reachable channels behavior is the default "general"
channel that CreateServerUseCase creates internally when a server is created,
plus the update/delete endpoints exercised below. Channel-membership/
message-permission behavior is covered in tests/integration/messages/
test_messages.py, where SendChannelMessageCommand actually lives.
"""

from datetime import UTC
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.infrastructure.persistence.models import ChannelOrm
from src.modules.users.domain.entities.user import User


async def _create_server_channel(
    authed_client: AsyncClient, session: AsyncSession, name: str = "Update Server"
) -> tuple[str, str]:
    response = await authed_client.post("/api/v1/servers", json={"name": name})
    assert response.status_code == 201
    server_id = response.json()["id"]

    result = await session.execute(
        select(ChannelOrm).where(ChannelOrm.server_id == UUID(server_id))
    )
    channel = result.scalar_one()
    return server_id, str(channel.id)


def _id(candidate: ChannelOrm) -> str:
    return str(candidate.id)


async def _seed_extra_channel(
    session: AsyncSession, server_id: str, name: str = "extra"
) -> str:
    from datetime import datetime

    stmt = insert(ChannelOrm).values(
        id=uuid4(),
        server_id=UUID(server_id),
        type="text",
        name=name,
        topic=None,
        position=1,
        last_sequence=0,
        is_private=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    await session.execute(stmt)
    await session.commit()

    result = await session.execute(
        select(ChannelOrm).where(
            ChannelOrm.server_id == UUID(server_id), ChannelOrm.name == name
        )
    )
    return _id(result.scalar_one())


class TestChannelAutoCreation:
    async def test_creating_a_server_creates_a_general_channel(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        response = await authed_client.post(
            "/api/v1/servers",
            json={"name": "Channel Auto-Create Server"},
        )
        assert response.status_code == 201
        server_id = response.json()["id"]

        result = await session.execute(
            select(ChannelOrm).where(ChannelOrm.server_id == UUID(server_id))
        )
        channels = result.scalars().all()

        assert len(channels) == 1
        channel = channels[0]
        assert channel.name == "general"
        assert channel.type == "text"
        assert channel.is_private is False
        assert channel.position == 0
        assert channel.last_sequence == 0


class TestUpdateChannel:
    async def test_success(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(authed_client, session)

        response = await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "name": "renamed", "topic": "new topic"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == channel_id
        assert data["name"] == "renamed"
        assert data["topic"] == "new topic"
        assert data["server_id"] == server_id

    async def test_partial_update(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(authed_client, session)

        response = await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "topic": "only topic"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "general"
        assert data["topic"] == "only topic"

    async def test_empty_topic_clears_field(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(authed_client, session)

        await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "topic": "some topic"},
        )
        response = await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "topic": ""},
        )
        assert response.status_code == 200
        assert response.json()["topic"] is None

    async def test_updated_at_refreshed(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(authed_client, session)

        result = await session.execute(
            select(ChannelOrm).where(ChannelOrm.id == UUID(channel_id))
        )
        channel = result.scalar_one()
        before = channel.updated_at

        await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "name": "touched"},
        )

        await session.refresh(channel)
        assert channel.updated_at > before

    async def test_name_conflict(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(authed_client, session)
        extra_channel_id = await _seed_extra_channel(session, server_id, "taken")
        assert extra_channel_id

        response = await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "name": "taken"},
        )
        assert response.status_code == 409

    async def test_not_found(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, _ = await _create_server_channel(authed_client, session)

        response = await authed_client.patch(
            f"/api/v1/channels/{uuid4()}",
            json={"server_id": server_id, "name": "renamed"},
        )
        assert response.status_code == 404

    async def test_server_mismatch(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        _, channel_id = await _create_server_channel(authed_client, session)

        response = await authed_client.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": str(uuid4()), "name": "renamed"},
        )
        assert response.status_code == 404

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        session: AsyncSession,
        get_all_users: list[User],
    ) -> None:
        server_id, channel_id = await _create_server_channel(
            authed_client, session, "Owned Server"
        )

        monica = get_all_users[1]
        await ac.post(
            "/api/v1/auth/login",
            json={"username": str(monica.username), "password": "12345678"},
        )
        response = await ac.patch(
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id, "name": "renamed"},
        )
        assert response.status_code == 403

    async def test_unauthorized(
        self,
        ac: AsyncClient,
        session: AsyncSession,
    ) -> None:
        response = await ac.patch(
            f"/api/v1/channels/{uuid4()}",
            json={"server_id": str(uuid4()), "name": "renamed"},
        )
        assert response.status_code == 401


class TestDeleteChannel:
    async def test_success_removes_extra_channel(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, _ = await _create_server_channel(
            authed_client, session, "Delete Server"
        )
        channel_id = await _seed_extra_channel(session, server_id)

        response = await authed_client.request(
            "DELETE",
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id},
        )
        assert response.status_code == 204

        result = await session.execute(
            select(ChannelOrm).where(ChannelOrm.id == UUID(channel_id))
        )
        assert result.scalar_one_or_none() is None

    async def test_last_channel_rejected(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, channel_id = await _create_server_channel(
            authed_client, session, "Last Channel Server"
        )

        response = await authed_client.request(
            "DELETE",
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id},
        )
        assert response.status_code == 422

    async def test_not_found(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        server_id, _ = await _create_server_channel(authed_client, session)

        response = await authed_client.request(
            "DELETE",
            f"/api/v1/channels/{uuid4()}",
            json={"server_id": server_id},
        )
        assert response.status_code == 404

    async def test_server_mismatch(
        self,
        authed_client: AsyncClient,
        session: AsyncSession,
    ) -> None:
        _, channel_id = await _create_server_channel(authed_client, session)

        response = await authed_client.request(
            "DELETE",
            f"/api/v1/channels/{channel_id}",
            json={"server_id": str(uuid4())},
        )
        assert response.status_code == 404

    async def test_not_owner(
        self,
        authed_client: AsyncClient,
        ac: AsyncClient,
        session: AsyncSession,
        get_all_users: list[User],
    ) -> None:
        server_id, _ = await _create_server_channel(
            authed_client, session, "Delete Owner Server"
        )
        channel_id = await _seed_extra_channel(session, server_id)

        monica = get_all_users[1]
        await ac.post(
            "/api/v1/auth/login",
            json={"username": str(monica.username), "password": "12345678"},
        )
        response = await ac.request(
            "DELETE",
            f"/api/v1/channels/{channel_id}",
            json={"server_id": server_id},
        )
        assert response.status_code == 403

    async def test_unauthorized(
        self,
        ac: AsyncClient,
        session: AsyncSession,
    ) -> None:
        response = await ac.request(
            "DELETE",
            f"/api/v1/channels/{uuid4()}",
            json={"server_id": str(uuid4())},
        )
        assert response.status_code == 401
