from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.channels.public.facade import ChannelsFacade
from src.modules.servers.domain.entities.dtos import (
    ServerCreate,
    ServerCreateData,
    ServerMemberCreate,
)
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.modules.servers.usecases.realtime import join_members_to_server_room
from src.shared.domain.transaction import Transaction


class CreateServerUseCase:
    def __init__(
        self,
        tx: Transaction,
        server_repository: ServerRepository,
        server_member_repository: ServerMemberRepository,
        channels_facade: ChannelsFacade,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._tx = tx
        self._servers = server_repository
        self._server_members = server_member_repository
        self._channels_facade = channels_facade
        self._room_membership_updater = room_membership_updater

    async def __call__(
        self, *, server_data: ServerCreateData, owner_id: UUID
    ) -> Server:
        _server_data = ServerCreate(
            name=server_data.name,
            description=server_data.description,
            owner_id=owner_id,
        )
        server = await self._servers.create(_server_data)

        member_data = ServerMemberCreate(
            user_id=owner_id,
            server_id=server.id,
            role=ServerMemberRole.owner,
        )
        await self._server_members.create(member_data)

        # CreateChannelUseCase never commits itself (see its docstring), so
        # this write lands in the same commit below.
        await self._channels_facade.create_default_channel(server.id)

        await self._tx.commit()
        await join_members_to_server_room(
            self._room_membership_updater,
            server.id,
            [owner_id],
        )
        return server
