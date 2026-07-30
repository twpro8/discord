from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from src.modules.channels.domain.entities.schemas import ChannelDTO
from src.modules.channels.domain.enums import ChannelType
from src.modules.servers.domain import services as server_permission_services
from src.modules.servers.domain.entities.server import (
    Server,
    ServerCreate,
    ServerUpdate,
    ServerUserSummary,
)
from src.modules.servers.domain.entities.server_invite import (
    ServerInvite,
    ServerInviteCreate,
)
from src.modules.servers.domain.entities.server_member import (
    ServerMember,
    ServerMemberCreate,
    ServerMemberUpdate,
)
from src.modules.servers.domain.repositories.server_unit_of_work import ServerUnitOfWork
from src.shared.errors import LumiereError
from src.shared.result import Result

# ServerMemberOrm has left_at/joined_at columns that the domain ServerMember
# entity never exposed (pre-existing gap) — callers still filter on left_at
# via the untyped get_one(**filter_by), so fakes must accept and ignore it.
_ENTITY_ONLY_FILTER_KEYS = {"left_at"}


def _matches(entity: object, filter_by: dict[str, Any]) -> bool:
    return all(
        getattr(entity, key) == value
        for key, value in filter_by.items()
        if key not in _ENTITY_ONLY_FILTER_KEYS
    )


class FakeServerRepository:
    def __init__(self) -> None:
        self.servers: dict[UUID, Server] = {}

    async def create(self, data: ServerCreate) -> Server:
        now = datetime.now(UTC)
        server = Server(
            id=uuid4(),
            name=data.name,
            description=data.description,
            icon_url=None,
            owner_id=data.owner_id,
            member_count=0,
            created_at=now,
            updated_at=now,
        )
        self.servers[server.id] = server
        return server

    async def get_one(self, **filter_by: Any) -> Server | None:
        return next((s for s in self.servers.values() if _matches(s, filter_by)), None)

    async def update(
        self,
        server_id: UUID,
        data: ServerUpdate,
        exclude_unset: bool = False,
    ) -> Server:
        server = self.servers[server_id]
        updates = data.model_dump(exclude_unset=exclude_unset, exclude={"id"})
        for key, value in updates.items():
            setattr(server, key, value)
        server.updated_at = datetime.now(UTC)
        return server

    async def delete(self, server_id: UUID) -> None:
        self.servers.pop(server_id, None)

    async def decrement_member_count(self, server_id: UUID) -> Server:
        server = self.servers[server_id]
        server.member_count -= 1
        return server

    async def increment_count(self, server_id: UUID) -> Server:
        server = self.servers[server_id]
        server.member_count += 1
        return server

    async def get_servers_where_user_is_member(
        self, user_id: UUID
    ) -> list[ServerUserSummary]:
        return []

    async def get_server_where_user_is_member(
        self, user_id: UUID, server_id: UUID
    ) -> Server | None:
        return self.servers.get(server_id)

    async def get_filtered(
        self, limit: int, offset: int, **filter_by: Any
    ) -> Sequence[Server]:
        matches = [s for s in self.servers.values() if _matches(s, filter_by)]
        return matches[offset : offset + limit]


class FakeServerMemberRepository:
    def __init__(self) -> None:
        self.members: dict[UUID, ServerMember] = {}

    async def create(self, data: ServerMemberCreate) -> ServerMember:
        member = ServerMember(
            id=uuid4(),
            server_id=data.server_id,
            user_id=data.user_id,
            role=data.role,
        )
        self.members[member.id] = member
        return member

    async def get_one(self, **filter_by: Any) -> ServerMember | None:
        return next((m for m in self.members.values() if _matches(m, filter_by)), None)

    async def update(
        self,
        id_: UUID,
        data: ServerMemberUpdate,
        exclude_unset: bool = False,
    ) -> ServerMember:
        member = self.members[id_]
        member.role = data.role
        return member


class FakeServersFacade:
    def __init__(self, server_members: FakeServerMemberRepository) -> None:
        self._server_members = server_members

    async def assert_is_server_member(self, user_id: UUID, server_id: UUID) -> None:
        await server_permission_services.assert_is_server_member(
            self._server_members, user_id, server_id
        )


class FakeServerInviteRepository:
    def __init__(self) -> None:
        self.invites: dict[UUID, ServerInvite] = {}

    async def create(self, data: ServerInviteCreate) -> ServerInvite:
        now = datetime.now(UTC)
        invite = ServerInvite(
            id=uuid4(),
            server_id=data.server_id,
            code=data.code,
            created_by=data.created_by,
            max_uses=data.max_uses,
            use_count=0,
            expires_at=data.expires_at,
            created_at=now,
        )
        self.invites[invite.id] = invite
        return invite

    async def get_one(self, **filter_by: Any) -> ServerInvite | None:
        return next((i for i in self.invites.values() if _matches(i, filter_by)), None)

    async def delete(self, invite_id: UUID) -> None:
        self.invites.pop(invite_id, None)

    async def get_filtered(
        self, limit: int, offset: int, **filter_by: Any
    ) -> Sequence[ServerInvite]:
        matches = [i for i in self.invites.values() if _matches(i, filter_by)]
        return matches[offset : offset + limit]

    async def increment_use_count_atomic(
        self, invite_id: UUID, max_uses: int | None
    ) -> int:
        invite = self.invites.get(invite_id)
        if invite is None:
            return 0
        if max_uses is not None and invite.use_count >= max_uses:
            return 0
        invite.use_count += 1
        return 1


class FakeServerUnitOfWork(ServerUnitOfWork):
    def __init__(
        self,
        servers: FakeServerRepository,
        server_members: FakeServerMemberRepository,
        invites: FakeServerInviteRepository,
    ) -> None:
        self.servers = servers
        self.server_members = server_members
        self.invites = invites
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FakeChannelsFacade:
    """Stand-in for channels' ChannelsFacade — CreateServerCommandHandler
    calls .create_default_channel() and never inspects the return value."""

    def __init__(self) -> None:
        self.calls: list[tuple[UUID, str]] = []

    async def create_default_channel(
        self, server_id: UUID
    ) -> Result[ChannelDTO, LumiereError]:
        self.calls.append((server_id, "general"))
        now = datetime.now(UTC)
        return Result.ok(
            ChannelDTO(
                id=uuid4(),
                name="general",
                server_id=server_id,
                type=ChannelType.text,
                topic=None,
                position=0,
                last_sequence=0,
                is_private=False,
                created_at=now,
                updated_at=now,
            )
        )
