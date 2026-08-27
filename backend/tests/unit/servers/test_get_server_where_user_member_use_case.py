from uuid import uuid4

import pytest

from src.core.realtime.rooms import server_room
from src.modules.servers.domain.entities.dtos import ServerCreate
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.usecases.get_server_where_user_member import (
    GetServerWhereUserMemberUseCase,
)
from tests.unit.servers.fakes import FakeRoomMembershipUpdater, FakeServerRepository


async def test_rejects_when_server_not_found_for_user() -> None:
    servers = FakeServerRepository()
    use_case = GetServerWhereUserMemberUseCase(servers, FakeRoomMembershipUpdater())

    with pytest.raises(ServerNotFoundError):
        await use_case(user_id=uuid4(), server_id=uuid4())


async def test_returns_server_when_found() -> None:
    servers = FakeServerRepository()
    server = await servers.create(ServerCreate(name="S", owner_id=uuid4()))
    room_membership_updater = FakeRoomMembershipUpdater()
    use_case = GetServerWhereUserMemberUseCase(servers, room_membership_updater)
    user_id = uuid4()

    result = await use_case(user_id=user_id, server_id=server.id)

    assert result.id == server.id
    assert room_membership_updater.joined == [(user_id, server_room(server.id))]
