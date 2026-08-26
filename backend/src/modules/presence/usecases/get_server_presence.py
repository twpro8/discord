from uuid import UUID

from src.modules.presence.domain.entities.dtos import PresenceDTO
from src.modules.presence.domain.repositories.presence_repository import (
    PresenceRepository,
)
from src.modules.servers.public.facade import ServersFacade


class GetServerPresenceUseCase:
    def __init__(
        self,
        presence_repository: PresenceRepository,
        servers_facade: ServersFacade,
    ) -> None:
        self._presence = presence_repository
        self._servers_facade = servers_facade

    async def __call__(
        self, *, server_id: UUID, requesting_user_id: UUID
    ) -> list[PresenceDTO]:
        await self._servers_facade.assert_is_server_member(
            requesting_user_id, server_id
        )

        member_ids = await self._servers_facade.list_server_member_ids(server_id)
        statuses = await self._presence.get_statuses(member_ids)
        return list(statuses.values())
