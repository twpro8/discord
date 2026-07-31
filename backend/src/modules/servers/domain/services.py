from uuid import UUID

from src.modules.servers.domain.entities.server import Server
from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.exceptions import (
    NotServerMemberError,
    NotServerOwnerError,
    ServerNotFoundError,
)
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)
from src.modules.servers.domain.repositories.server_repository import ServerRepository


async def assert_is_server_member(
    server_members: ServerMemberRepository,
    user_id: UUID,
    server_id: UUID,
) -> ServerMember:
    member = await server_members.get_one(server_id=server_id, user_id=user_id)
    if member is None:
        raise NotServerMemberError
    return member


async def assert_is_server_owner(
    server_members: ServerMemberRepository,
    servers: ServerRepository,
    user_id: UUID,
    server_id: UUID,
) -> Server:
    await assert_is_server_member(server_members, user_id, server_id)
    server = await servers.get_one(id=server_id)
    if server is None:
        raise ServerNotFoundError
    if server.owner_id != user_id:
        raise NotServerOwnerError
    return server
