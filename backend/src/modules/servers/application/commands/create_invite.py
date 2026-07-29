import secrets
import string
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.modules.servers.domain.entities.server_invite import (
    ServerInvite,
    ServerInviteCreate,
    ServerInviteCreateRequest,
)
from src.modules.servers.domain.exceptions import (
    ServerInviteGenerationFailedError,
    ServerInvitePermissionDeniedError,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


def _generate_random_code(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass(frozen=True, kw_only=True)
class CreateInviteCommand(Command):
    server_id: UUID
    user_id: UUID
    payload: ServerInviteCreateRequest


class CreateInviteCommandHandler:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: CreateInviteCommand
    ) -> Result[ServerInvite, LumiereError]:
        server_id, user_id, payload = (
            command.server_id,
            command.user_id,
            command.payload,
        )
        server = await self._uow.servers.get_one(id=server_id, owner_id=user_id)
        if not server:
            return Result.err(ServerInvitePermissionDeniedError())

        expires_at = None
        if payload.expires_in is not None:
            expires_at = datetime.now(UTC) + timedelta(seconds=payload.expires_in)

        code = None
        for _ in range(3):
            potential_code = _generate_random_code(8)
            exists = await self._uow.invites.get_one(code=potential_code)
            if not exists:
                code = potential_code
                break

        if not code:
            return Result.err(ServerInviteGenerationFailedError())

        db_payload = ServerInviteCreate(
            **payload.model_dump(),
            server_id=server_id,
            created_by=user_id,
            code=code,
            expires_at=expires_at,
        )

        invite = await self._uow.invites.create(db_payload)
        await self._uow.commit()
        return Result.ok(invite)
