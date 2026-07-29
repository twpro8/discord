"""Integration tests for channels.

Channels have no CRUD surface of their own yet (no update/delete/list
endpoints, no permission enforcement beyond message-sending) — that is a
pre-existing product gap tracked separately, not covered here. The only
currently-reachable channels behavior is the default "general" channel
that CreateServerCommand creates internally when a server is created.
Channel-membership/message-permission behavior is covered in
tests/integration/messages/test_messages.py, where SendChannelMessageCommand
actually lives.
"""

from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.channels.infrastructure.persistence.models import ChannelOrm


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
