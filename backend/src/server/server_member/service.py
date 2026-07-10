from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.server.enums import ServerMemberRole
from src.server.exceptions import MemberNotFoundError
from src.server.invite.exceptions import ServerInviteNotFoundError
from src.server.server_member.schemas import (
    ServerMemberCreateSchema,
    ServerMemberSchema,
    ServerMemberUpdateSchema,
    UpdateMemberRole,
)
from src.server.server_member.unit_of_work import ServerMemberUnitOfWork


class ServerMemberService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_member_unit_of_work: ServerMemberUnitOfWork,
    ) -> None:
        super().__init__(session)
        self.uow = server_member_unit_of_work

    async def create_member(
        self,
        user_id: UUID,
        server_id: UUID,
        role: ServerMemberRole = ServerMemberRole.member,
        is_commit: bool = True,
    ) -> ServerMemberSchema:
        member_data = ServerMemberCreateSchema(
            server_id=server_id,
            user_id=user_id,
            role=role,
        )

        member = await self.uow.server_members.create(member_data)
        if is_commit:
            await self.uow.commit()

        return member

    async def get_one(self, **filter_by: Any) -> ServerMemberSchema | None:
        return await self.uow.server_members.get_one(**filter_by)

    async def mark_as_left(
        self, server_member_id: UUID, left_at: datetime
    ) -> ServerMemberSchema:
        member = await self.get_one(id=server_member_id)
        if not member:
            raise MemberNotFoundError

        update_schema = ServerMemberUpdateSchema(left_at=left_at)
        state = await self.uow.server_members.update(server_member_id, update_schema)
        await self.uow.commit()
        return state

    async def update_role(
        self, server_member_id: UUID, role: ServerMemberRole
    ) -> ServerMemberSchema:
        member = await self.get_one(id=server_member_id)
        if not member:
            raise MemberNotFoundError

        update_schema = UpdateMemberRole(role=role)
        state = await self.uow.server_members.update(server_member_id, update_schema)
        await self.uow.commit()
        return state

    async def join_server(self, user_id: UUID, code: str) -> ServerMemberSchema:
        invite = await self.uow.invites.get_one(code=code)
        if not invite:
            raise ServerInviteNotFoundError

        now = datetime.now(timezone.utc)
        if invite.expires_at is not None:
            expires_at = (
                invite.expires_at.replace(tzinfo=timezone.utc)
                if invite.expires_at.tzinfo is None
                else invite.expires_at
            )
            if now > expires_at:
                raise ServerInviteNotFoundError

        member = await self.uow.server_members.get_one(
            server_id=invite.server_id, user_id=user_id, left_at=None
        )
        if member:
            return member

        affected_rows = await self.uow.invites.increment_use_count_atomic(
            invite_id=invite.id, max_uses=invite.max_uses
        )

        if affected_rows == 0:
            raise ServerInviteNotFoundError

        await self.uow.servers.increment_count(invite.server_id)

        member_data = ServerMemberCreateSchema(
            server_id=invite.server_id,
            user_id=user_id,
            role=ServerMemberRole.member,
        )
        member = await self.uow.server_members.create(member_data)
        await self.uow.commit()
        return member
