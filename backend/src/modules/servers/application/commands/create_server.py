from dataclasses import dataclass
from uuid import UUID

from src.core.websocket.manager import RoomMembershipUpdater
from src.modules.channels.public.facade import ChannelsFacade
from src.modules.servers.application.realtime import join_members_to_server_room
from src.modules.servers.domain.entities.dtos import (
    ServerCreate,
    ServerCreateData,
    ServerMemberCreate,
)
from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class CreateServerCommand(Command):
    server_data: ServerCreateData
    owner_id: UUID


class CreateServerCommandHandler:
    def __init__(
        self,
        uow: ServerUnitOfWork,
        channels_facade: ChannelsFacade,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._uow = uow
        self._channels_facade = channels_facade
        self._room_membership_updater = room_membership_updater

    async def handle(
        self, command: CreateServerCommand
    ) -> Result[Server, LumiereError]:
        server_data, owner_id = command.server_data, command.owner_id
        _server_data = ServerCreate(
            name=server_data.name,
            description=server_data.description,
            owner_id=owner_id,
        )
        server = await self._uow.servers.create(_server_data)

        member_data = ServerMemberCreate(
            user_id=owner_id,
            server_id=server.id,
            role=ServerMemberRole.owner,
        )
        await self._uow.server_members.create(member_data)

        await self._channels_facade.create_default_channel(server.id)

        await self._uow.commit()
        await join_members_to_server_room(
            self._room_membership_updater,
            server.id,
            [owner_id],
        )
        return Result.ok(server)
