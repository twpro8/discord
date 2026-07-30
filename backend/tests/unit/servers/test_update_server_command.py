from uuid import uuid4

from src.modules.servers.application.commands.update_server import (
    UpdateServerCommand,
    UpdateServerCommandHandler,
)
from src.modules.servers.domain.entities.server import (
    ServerCreate,
    ServerUpdateData,
)
from src.modules.servers.domain.exceptions import ServerNotFoundError
from tests.unit.servers.fakes import (
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


def _handler() -> tuple[UpdateServerCommandHandler, FakeServerRepository]:
    servers = FakeServerRepository()
    uow = FakeServerUnitOfWork(
        servers, FakeServerMemberRepository(), FakeServerInviteRepository()
    )
    return UpdateServerCommandHandler(uow), servers


async def test_rejects_unknown_server() -> None:
    handler, _ = _handler()

    result = await handler.handle(
        UpdateServerCommand(
            update_data=ServerUpdateData(name="New"),
            server_id=uuid4(),
            owner_id=uuid4(),
        )
    )

    assert result.is_err
    assert isinstance(result.error, ServerNotFoundError)


async def test_partial_update_only_touches_provided_fields() -> None:
    handler, servers = _handler()
    owner_id = uuid4()
    server = await servers.create(
        ServerCreate(name="Original", description="Keep me", owner_id=owner_id)
    )

    result = await handler.handle(
        UpdateServerCommand(
            update_data=ServerUpdateData(name="Only Name Changed"),
            server_id=server.id,
            owner_id=owner_id,
        )
    )

    assert result.is_ok
    assert result.value.name == "Only Name Changed"
    assert result.value.description == "Keep me"
