from uuid import UUID

from src.modules.servers.domain.entities.server_member import ServerMember
from src.modules.servers.domain.exceptions import NotServerMemberError
from src.modules.servers.domain.repositories.server_member_repository import (
    ServerMemberRepository,
)


async def assert_is_server_member(
    server_members: ServerMemberRepository,
    user_id: UUID,
    server_id: UUID,
) -> ServerMember:
    member = await server_members.get_one(server_id=server_id, user_id=user_id)
    if member is None:
        raise NotServerMemberError
    return member
