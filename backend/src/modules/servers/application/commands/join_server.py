from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from src.modules.servers.domain.entities.server_member import (
    ServerMember,
    ServerMemberCreate,
)
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import ServerInviteNotFoundError
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.application.command import Command
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class JoinServerCommand(Command):
    user_id: UUID
    code: str


class JoinServerCommandHandler:
    def __init__(self, uow: ServerUnitOfWork) -> None:
        self._uow = uow

    async def handle(
        self, command: JoinServerCommand
    ) -> Result[ServerMember, ServerInviteNotFoundError]:
        user_id = command.user_id
        code = command.code
        invite = await self._uow.invites.get_one(code=code)
        if not invite:
            return Result.err(ServerInviteNotFoundError())

        now = datetime.now(UTC)
        if invite.expires_at is not None:
            expires_at = (
                invite.expires_at.replace(tzinfo=UTC)
                if invite.expires_at.tzinfo is None
                else invite.expires_at
            )
            if now > expires_at:
                return Result.err(ServerInviteNotFoundError())

        member = await self._uow.server_members.get_one(
            server_id=invite.server_id, user_id=user_id, left_at=None
        )
        if member:
            return Result.ok(member)

        affected_rows = await self._uow.invites.increment_use_count_atomic(
            invite_id=invite.id, max_uses=invite.max_uses
        )

        if affected_rows == 0:
            return Result.err(ServerInviteNotFoundError())

        await self._uow.servers.increment_count(invite.server_id)

        member_data = ServerMemberCreate(
            server_id=invite.server_id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
        member = await self._uow.server_members.create(member_data)
        await self._uow.commit()
        return Result.ok(member)
