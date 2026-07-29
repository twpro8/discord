from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from src.modules.servers.domain.exceptions import NotServerMemberError

if TYPE_CHECKING:
    from src.modules.servers.domain.entities.server_member import ServerMember
    from src.modules.servers.domain.repositories.server_member_repository import (
        ServerMemberRepository,
    )


class SupportsServerMemberPermissions(Protocol):
    server_members: ServerMemberRepository


async def assert_is_server_member(
    uow: SupportsServerMemberPermissions,
    user_id: UUID,
    server_id: UUID,
) -> ServerMember:
    member = await uow.server_members.get_one(server_id=server_id, user_id=user_id)
    if member is None:
        raise NotServerMemberError
    return member
