from datetime import UTC, datetime
from uuid import UUID

from src.core.realtime.manager import RoomMembershipUpdater
from src.modules.servers.domain.entities.dtos import ServerMemberCreate
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import ServerInviteNotFoundError
from src.modules.servers.domain.repositories.server_invite_repository import (
    ServerInviteRepository,
)
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.modules.servers.usecases.realtime import join_members_to_server_room
from src.shared.domain.transaction import Transaction


class JoinServerUseCase:
    def __init__(
        self,
        tx: Transaction,
        server_repository: ServerRepository,
        server_member_repository: ServerMemberRepository,
        server_invite_repository: ServerInviteRepository,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._tx = tx
        self._servers = server_repository
        self._server_members = server_member_repository
        self._invites = server_invite_repository
        self._room_membership_updater = room_membership_updater

    async def __call__(self, *, user_id: UUID, code: str) -> ServerMember:
        invite = await self._invites.get_one(code=code)
        if not invite:
            raise ServerInviteNotFoundError

        now = datetime.now(UTC)
        if invite.expires_at is not None:
            expires_at = (
                invite.expires_at.replace(tzinfo=UTC)
                if invite.expires_at.tzinfo is None
                else invite.expires_at
            )
            if now > expires_at:
                raise ServerInviteNotFoundError

        member = await self._server_members.get_one(
            server_id=invite.server_id, user_id=user_id, left_at=None
        )
        if member:
            await join_members_to_server_room(
                self._room_membership_updater,
                invite.server_id,
                [user_id],
            )
            return member

        affected_rows = await self._invites.increment_use_count_atomic(
            invite_id=invite.id, max_uses=invite.max_uses
        )

        if affected_rows == 0:
            raise ServerInviteNotFoundError

        await self._servers.increment_count(invite.server_id)

        member_data = ServerMemberCreate(
            server_id=invite.server_id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
        member = await self._server_members.create(member_data)
        await self._tx.commit()
        await join_members_to_server_room(
            self._room_membership_updater,
            invite.server_id,
            [user_id],
        )
        return member
