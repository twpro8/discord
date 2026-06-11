from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.services import BaseService
from src.server.enums import ServerMemberRole
from src.server.schemas import (
    ServerCreateRequestSchema,
    ServerCreateSchema,
    ServerSchema,
    ServerUpdateRequestSchema,
    ServerUpdateSchema,
)
from src.channel.service import ChannelService
from src.server.server_member.service import ServerMemberService
from src.server.exceptions import (
    CannotKickSelfError,
    MemberNotFoundError,
    OnlyOwnerCanKickError,
    OwnerCannotLeaveServerError,
    ServerNotFoundError,
    ServerNotEmptyError,
)
from src.server.unit_of_work import ServerUnitOfWork


class ServerService(BaseService):
    def __init__(
        self,
        session: AsyncSession,
        server_unit_of_work: ServerUnitOfWork,
        channel_service: ChannelService,
        server_member_service: ServerMemberService,
    ) -> None:
        super().__init__(session)
        self.uow = server_unit_of_work
        self.channel_service = channel_service
        self.server_member_service = server_member_service

    async def create_server(
        self,
        server_data: ServerCreateRequestSchema,
        owner_id: UUID,
    ) -> ServerSchema:
        # Creating server
        _server_data = ServerCreateSchema(**server_data.model_dump(), owner_id=owner_id)
        server = await self.uow.servers.create(_server_data)

        # Adding owner to server members
        await self.server_member_service.create_member(
            user_id=owner_id,
            server_id=server.id,
            role=ServerMemberRole.owner,
            is_commit=False,
        )

        # Creating general channel for server
        await self.channel_service.create_channel(
            server.id,
            name="general",
            is_commit=False,
        )

        await self.uow.commit()
        return server

    async def update_server(
        self,
        update_data: ServerUpdateRequestSchema,
        server_id: UUID,
        owner_id: UUID,
    ) -> ServerSchema:
        server = await self.uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        _update_data = ServerUpdateSchema(
            **update_data.model_dump(),
            id=server.id,
            owner_id=owner_id,
        )
        updated_server = await self.uow.servers.update(server.id, _update_data)

        await self.uow.commit()
        return updated_server

    async def delete_server(
        self,
        server_id: UUID,
        owner_id: UUID,
    ) -> None:
        server = await self.uow.servers.get_one(id=server_id, owner_id=owner_id)
        if not server:
            raise ServerNotFoundError

        if server.member_count > 1:
            raise ServerNotEmptyError

        await self.uow.servers.delete(server.id)
        await self.uow.commit()

    async def kick_member(
        self,
        server_id: UUID,
        request_user_id: UUID,
        target_user_id: UUID,
    ) -> None:
        """
        Method for kicking a user from the server

        Steps:
        1. A user can't kick themselves.
        2. Check that the server exists.
        3. Check that the user has permission to kick (currently, only the owner can kick).
        4. Check that the user being kicked is a server partner.
        5. Kick the users (update left_at).
        6. Decrease the user counter in the region.
        """

        if request_user_id == target_user_id:
            raise CannotKickSelfError

        server = await self.uow.servers.get_one(id=server_id)
        if not server:
            raise ServerNotFoundError

        if server.owner_id != request_user_id:
            raise OnlyOwnerCanKickError

        member = await self.server_member_service.get_one(
            server_id=server_id,
            user_id=target_user_id,
            left_at=None,
        )

        if not member:
            raise MemberNotFoundError

        await self.server_member_service.update(
            server_member_id=member.id,
            left_at=datetime.now(timezone.utc),
        )
        await self.uow.servers.decrement_member_count(server.id)
        await self.uow.commit()

    async def leave_server(
        self,
        server_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Method for leaving the server

        Steps:
        1. Check that the server exists.
        2. Check that the user is a member of the server.
        3. A owner can't leave the server, they can only delete it.
        4. Update left_at for the user.
        5. Decrease the user counter in the region.
        """

        server = await self.uow.servers.get_one(id=server_id)
        if not server:
            raise ServerNotFoundError

        if server.owner_id == user_id:
            raise OwnerCannotLeaveServerError

        member = await self.server_member_service.get_one(
            server_id=server_id,
            user_id=user_id,
            left_at=None,
        )

        if not member:
            raise MemberNotFoundError

        await self.server_member_service.update(
            server_member_id=member.id,
            left_at=datetime.now(timezone.utc),
        )
        await self.uow.servers.decrement_member_count(server.id)
        await self.uow.commit()
