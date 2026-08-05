from dataclasses import dataclass
from uuid import UUID

from src.modules.servers.domain import services
from src.modules.servers.domain.entities.dtos import ServerMemberWithUser
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.shared.application.query import Query
from src.shared.errors import LumiereError
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetServerMembersQuery(Query):
    server_id: UUID
    requesting_user_id: UUID


class GetServerMembersQueryHandler:
    def __init__(self, server_member_repository: ServerMemberRepository) -> None:
        self._server_members = server_member_repository

    async def handle(
        self, query: GetServerMembersQuery
    ) -> Result[list[ServerMemberWithUser], LumiereError]:
        try:
            await services.assert_is_server_member(
                self._server_members, query.requesting_user_id, query.server_id
            )
        except LumiereError as error:
            return Result.err(error)

        members = await self._server_members.list_with_users(query.server_id)
        return Result.ok(members)
