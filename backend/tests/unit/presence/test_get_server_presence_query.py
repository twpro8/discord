from uuid import uuid4

from src.modules.presence.application.queries.get_server_presence import (
    GetServerPresenceQuery,
    GetServerPresenceQueryHandler,
)
from src.modules.presence.domain.entities.dtos import PresenceDTO, PresenceStatus
from src.modules.servers.domain.entities.dtos import ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import NotServerMemberError
from tests.unit.presence.fakes import FakePresenceRepository
from tests.unit.servers.fakes import (
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServersFacade,
)


async def test_rejects_non_members() -> None:
    presence = FakePresenceRepository()
    servers_facade = FakeServersFacade(
        FakeServerMemberRepository(), FakeServerRepository()
    )
    handler = GetServerPresenceQueryHandler(presence, servers_facade)

    result = await handler.handle(
        GetServerPresenceQuery(server_id=uuid4(), requesting_user_id=uuid4())
    )

    assert result.is_err
    assert isinstance(result.error, NotServerMemberError)


async def test_returns_presence_for_all_server_members() -> None:
    server_id = uuid4()
    requester_id, other_member_id = uuid4(), uuid4()
    members = FakeServerMemberRepository()
    await members.create(
        ServerMemberCreate(
            server_id=server_id, user_id=requester_id, role=ServerMemberRole.member
        )
    )
    await members.create(
        ServerMemberCreate(
            server_id=server_id, user_id=other_member_id, role=ServerMemberRole.member
        )
    )
    servers_facade = FakeServersFacade(members, FakeServerRepository())
    presence = FakePresenceRepository()
    presence.statuses = {
        requester_id: PresenceDTO(user_id=requester_id, status=PresenceStatus.ONLINE),
        other_member_id: PresenceDTO(
            user_id=other_member_id, status=PresenceStatus.AWAY
        ),
    }
    handler = GetServerPresenceQueryHandler(presence, servers_facade)

    result = await handler.handle(
        GetServerPresenceQuery(server_id=server_id, requesting_user_id=requester_id)
    )

    assert result.is_ok
    returned_ids = {dto.user_id for dto in result.value}
    assert returned_ids == {requester_id, other_member_id}
