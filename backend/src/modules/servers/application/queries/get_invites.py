from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from src.modules.servers.domain.entities.dtos import ServerInviteWithStatus
from src.modules.servers.domain.entities.server_invite import ServerInvite
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


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


@dataclass(frozen=True, kw_only=True)
class GetInvitesQuery(Query):
    user_id: UUID
    server_id: UUID
    limit: int = 100
    offset: int = 0


class GetInvitesQueryHandler:
    def __init__(
        self,
        server_repository: ServerRepository,
        server_invite_repository: ServerInviteRepository,
    ) -> None:
        self._server_repository = server_repository
        self._server_invite_repository = server_invite_repository

    async def handle(
        self, query: GetInvitesQuery
    ) -> Result[list[ServerInviteWithStatus], LumiereError]:
        server = await self._server_repository.get_one(
            id=query.server_id, owner_id=query.user_id
        )
        if not server:
            return Result.ok([])

        invites = await self._server_invite_repository.get_filtered(
            server_id=query.server_id,
            limit=query.limit,
            offset=query.offset,
        )
        return Result.ok(
            [
                ServerInviteWithStatus(
                    id=invite.id,
                    server_id=invite.server_id,
                    code=invite.code,
                    created_by=invite.created_by,
                    max_uses=invite.max_uses,
                    use_count=invite.use_count,
                    expires_at=invite.expires_at,
                    created_at=invite.created_at,
                    validity_status=_compute_validity_status(invite),
                )
                for invite in invites
            ]
        )
