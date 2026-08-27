from uuid import uuid4

import pytest

from src.modules.servers.domain.entities.dtos import ServerCreate, ServerUpdateData
from src.modules.servers.domain.exceptions import ServerNotFoundError
from src.modules.servers.usecases.update_server import UpdateServerUseCase
from tests.unit.servers.fakes import FakeServerRepository


def _use_case() -> tuple[UpdateServerUseCase, FakeServerRepository]:
    servers = FakeServerRepository()
    return UpdateServerUseCase(servers), servers


async def test_rejects_unknown_server() -> None:
    use_case, _ = _use_case()

    with pytest.raises(ServerNotFoundError):
        await use_case(
            update_data=ServerUpdateData(name="New"),
            server_id=uuid4(),
            owner_id=uuid4(),
        )


async def test_partial_update_only_touches_provided_fields() -> None:
    use_case, servers = _use_case()
    owner_id = uuid4()
    server = await servers.create(
        ServerCreate(name="Original", description="Keep me", owner_id=owner_id)
    )

    updated = await use_case(
        update_data=ServerUpdateData(name="Only Name Changed"),
        server_id=server.id,
        owner_id=owner_id,
    )

    assert updated.name == "Only Name Changed"
    assert updated.description == "Keep me"
