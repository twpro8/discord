from datetime import UTC, datetime
from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.servers.domain.entities.dtos import ServerMemberCreate
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import ServerInviteNotFoundError
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.modules.servers.usecases.realtime import join_members_to_server_room


class JoinServerUseCase:
    def __init__(
        self,
        uow: ServerUnitOfWork,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._uow = uow
        self._room_membership_updater = room_membership_updater

    async def __call__(self, *, user_id: UUID, code: str) -> ServerMember:
        invite = await self._uow.invites.get_one(code=code)
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

        member = await self._uow.server_members.get_one(
            server_id=invite.server_id, user_id=user_id, left_at=None
        )
        if member:
            await join_members_to_server_room(
                self._room_membership_updater,
                invite.server_id,
                [user_id],
            )
            return member

        affected_rows = await self._uow.invites.increment_use_count_atomic(
            invite_id=invite.id, max_uses=invite.max_uses
        )

        if affected_rows == 0:
            raise ServerInviteNotFoundError

        await self._uow.servers.increment_count(invite.server_id)

        member_data = ServerMemberCreate(
            server_id=invite.server_id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
        member = await self._uow.server_members.create(member_data)
        await self._uow.commit()
        await join_members_to_server_room(
            self._room_membership_updater,
            invite.server_id,
            [user_id],
        )
        return member
