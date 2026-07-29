from uuid import UUID

from src.modules.channels.application.commands.create_channel import (
    CreateChannelCommand,
)
from src.modules.servers.domain.entities.server import (
    Server,
    ServerCreate,
    ServerCreateRequest,
)
from src.modules.servers.domain.entities.server_member import (
    ServerMemberCreate,
)
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork


class CreateServerCommand:
    def __init__(
        self,
        uow: ServerUnitOfWork,
        create_channel_command: CreateChannelCommand,
    ) -> None:
        self._uow = uow
        self._create_channel_command = create_channel_command

    async def __call__(
        self,
        server_data: ServerCreateRequest,
        owner_id: UUID,
    ) -> Server:
        _server_data = ServerCreate(**server_data.model_dump(), owner_id=owner_id)
        server = await self._uow.servers.create(_server_data)

        member_data = ServerMemberCreate(
            user_id=owner_id,
            server_id=server.id,
            role=ServerMemberRole.owner,
        )
        await self._uow.server_members.create(member_data)

        await self._create_channel_command(
            server.id,
            name="general",
            is_commit=False,
        )

        await self._uow.commit()
        return server
