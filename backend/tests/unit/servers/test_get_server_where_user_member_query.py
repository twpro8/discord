from uuid import uuid4

from src.core.realtime.rooms import server_room
from src.modules.servers.application.queries.get_server_where_user_member import (
    GetServerWhereUserMemberQuery,
    GetServerWhereUserMemberQueryHandler,
)
from src.modules.servers.domain.entities.dtos import ServerCreate
from src.modules.servers.domain.exceptions import ServerNotFoundError
from tests.unit.servers.fakes import FakeRoomMembershipUpdater, FakeServerRepository


async def test_rejects_when_server_not_found_for_user() -> None:
    servers = FakeServerRepository()
    handler = GetServerWhereUserMemberQueryHandler(servers, FakeRoomMembershipUpdater())

    result = await handler.handle(
        GetServerWhereUserMemberQuery(user_id=uuid4(), server_id=uuid4())
    )

    assert result.is_err
    assert isinstance(result.error, ServerNotFoundError)


async def test_returns_server_when_found() -> None:
    servers = FakeServerRepository()
    server = await servers.create(ServerCreate(name="S", owner_id=uuid4()))
    room_membership_updater = FakeRoomMembershipUpdater()
    handler = GetServerWhereUserMemberQueryHandler(servers, room_membership_updater)
    user_id = uuid4()

    result = await handler.handle(
        GetServerWhereUserMemberQuery(user_id=user_id, server_id=server.id)
    )

    assert result.is_ok
    assert result.value.id == server.id
    assert room_membership_updater.joined == [(user_id, server_room(server.id))]
