from uuid import UUID

from src.modules.servers.domain import services
from src.modules.servers.domain.entities.dtos import ServerMemberWithUser
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)


class GetServerMembersUseCase:
    def __init__(self, server_member_repository: ServerMemberRepository) -> None:
        self._server_members = server_member_repository

    async def __call__(
        self, *, server_id: UUID, requesting_user_id: UUID
    ) -> list[ServerMemberWithUser]:
        await services.assert_is_server_member(
            self._server_members, requesting_user_id, server_id
        )

        return await self._server_members.list_with_users(server_id)
