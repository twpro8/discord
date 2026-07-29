from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from src.modules.servers.domain.entities.server_invite import (
    ServerInvite,
    ServerInviteWithStatus,
)
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


def _compute_validity_status(
    invite: ServerInvite,
) -> Literal["valid", "expired", "exhausted"]:
    now = datetime.now(UTC)

    if invite.max_uses is not None and invite.use_count >= invite.max_uses:
        return "exhausted"

    if invite.expires_at is not None:
        expires_at = (
            invite.expires_at.replace(tzinfo=UTC)
            if invite.expires_at.tzinfo is None
            else invite.expires_at
        )
        if now > expires_at:
            return "expired"

    return "valid"


class GetInvitesQuery:
    def __init__(
        self,
        server_repository: ServerRepository,
        server_invite_repository: ServerInviteRepository,
    ) -> None:
        self._server_repository = server_repository
        self._server_invite_repository = server_invite_repository

    async def __call__(
        self, user_id: UUID, server_id: UUID, limit: int = 100, offset: int = 0
    ) -> list[ServerInviteWithStatus]:
        server = await self._server_repository.get_one(id=server_id, owner_id=user_id)
        if not server:
            return []

        invites = await self._server_invite_repository.get_filtered(
            server_id=server_id,
            limit=limit,
            offset=offset,
        )
        return [
            ServerInviteWithStatus(
                **invite.model_dump(),
                validity_status=_compute_validity_status(invite),
            )
            for invite in invites
        ]
