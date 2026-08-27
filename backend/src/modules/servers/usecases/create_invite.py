import secrets
import string
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.modules.servers.domain.entities.dtos import (
    ServerInviteCreate,
    ServerInviteCreateData,
)
from src.modules.servers.domain.entities.server_invite import ServerInvite
from src.modules.servers.domain.exceptions import (
    ServerInviteGenerationFailedError,
    ServerInvitePermissionDeniedError,
)
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


def _generate_random_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class CreateInviteUseCase:
    def __init__(
        self,
        server_repository: ServerRepository,
        server_invite_repository: ServerInviteRepository,
    ) -> None:
        self._servers = server_repository
        self._invites = server_invite_repository

    async def __call__(
        self, *, server_id: UUID, user_id: UUID, payload: ServerInviteCreateData
    ) -> ServerInvite:
        server = await self._servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            raise ServerInvitePermissionDeniedError

        expires_at = None
        if payload.expires_in is not None:
            expires_at = datetime.now(UTC) + timedelta(seconds=payload.expires_in)

        code = None
        for _ in range(3):
            potential_code = _generate_random_code(8)
            exists = await self._invites.get_one(code=potential_code)
            if not exists:
                code = potential_code
                break

        if not code:
            raise ServerInviteGenerationFailedError

        db_payload = ServerInviteCreate(
            server_id=server_id,
            created_by=user_id,
            code=code,
            max_uses=payload.max_uses,
            expires_at=expires_at,
        )

        return await self._invites.create(db_payload)
