from uuid import uuid4

import pytest

from src.modules.presence.domain.entities.dtos import PresenceDTO, PresenceStatus
from src.modules.presence.usecases.get_server_presence import GetServerPresenceUseCase
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
    use_case = GetServerPresenceUseCase(presence, servers_facade)

    with pytest.raises(NotServerMemberError):
        await use_case(server_id=uuid4(), requesting_user_id=uuid4())


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
    use_case = GetServerPresenceUseCase(presence, servers_facade)

    result = await use_case(server_id=server_id, requesting_user_id=requester_id)

    returned_ids = {dto.user_id for dto in result}
    assert returned_ids == {requester_id, other_member_id}
