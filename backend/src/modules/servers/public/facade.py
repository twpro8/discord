from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.servers.domain import services
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository
from src.modules.servers.infrastructure.persistence.server_member_repository_impl import (
    ServerMemberRepositoryImpl,
)
from src.modules.servers.infrastructure.persistence.server_repository_impl import (
    ServerRepositoryImpl,
)


class ServersFacade(Protocol):
    """The only way other modules may check server membership/ownership.
    Raises servers' own domain exceptions (NotServerMemberError,
    NotServerOwnerError) — callers catch LumiereError at their own command
    boundary and convert to a Result, matching this codebase's established
    cross-module delegation convention."""

    async def assert_is_server_member(self, user_id: UUID, server_id: UUID) -> None: ...

    async def assert_is_server_owner(self, user_id: UUID, server_id: UUID) -> None: ...


class RepositoryBackedServersFacade:
    def __init__(
        self,
        server_member_repository: ServerMemberRepository,
        server_repository: ServerRepository,
    ) -> None:
        self._server_members = server_member_repository
        self._servers = server_repository

    async def assert_is_server_member(self, user_id: UUID, server_id: UUID) -> None:
        await services.assert_is_server_member(self._server_members, user_id, server_id)

    async def assert_is_server_owner(self, user_id: UUID, server_id: UUID) -> None:
        await services.assert_is_server_owner(
            self._server_members, self._servers, user_id, server_id
        )


def build_servers_facade(session: AsyncSession) -> ServersFacade:
    return RepositoryBackedServersFacade(
        ServerMemberRepositoryImpl(session), ServerRepositoryImpl(session)
    )
