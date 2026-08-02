from uuid import uuid4

from src.modules.servers.application.queries.get_server_where_user_member import (
    GetServerWhereUserMemberQuery,
    GetServerWhereUserMemberQueryHandler,
)
from src.modules.servers.domain.entities.dtos import ServerCreate
from src.modules.servers.domain.exceptions import ServerNotFoundError
from tests.unit.servers.fakes import FakeServerRepository


async def test_rejects_when_server_not_found_for_user() -> None:
    servers = FakeServerRepository()
    handler = GetServerWhereUserMemberQueryHandler(servers)

    result = await handler.handle(
        GetServerWhereUserMemberQuery(user_id=uuid4(), server_id=uuid4())
    )

    assert result.is_err
    assert isinstance(result.error, ServerNotFoundError)


async def test_returns_server_when_found() -> None:
    servers = FakeServerRepository()
    server = await servers.create(ServerCreate(name="S", owner_id=uuid4()))
    handler = GetServerWhereUserMemberQueryHandler(servers)

    result = await handler.handle(
        GetServerWhereUserMemberQuery(user_id=uuid4(), server_id=server.id)
    )

    assert result.is_ok
    assert result.value.id == server.id
