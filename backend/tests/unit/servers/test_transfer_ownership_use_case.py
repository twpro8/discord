from uuid import uuid4

import pytest

from src.modules.servers.domain.entities.dtos import ServerCreate, ServerMemberCreate
from src.modules.servers.domain.enums import ServerMemberRole
from src.modules.servers.domain.exceptions import (
    CannotTransferToSelfError,
    MemberNotFoundError,
    ServerNotFoundError,
    YouAreNotOwnerError,
)
from src.modules.servers.usecases.transfer_ownership import (
    TransferServerOwnershipUseCase,
)
from tests.unit.servers.fakes import (
    FakeServerInviteRepository,
    FakeServerMemberRepository,
    FakeServerRepository,
    FakeServerUnitOfWork,
)


def _seeded_uow() -> tuple[
    FakeServerUnitOfWork, FakeServerRepository, FakeServerMemberRepository
]:
    servers = FakeServerRepository()
    members = FakeServerMemberRepository()
    uow = FakeServerUnitOfWork(servers, members, FakeServerInviteRepository())
    return uow, servers, members


async def test_rejects_unknown_server() -> None:
    uow, _, _ = _seeded_uow()
    use_case = TransferServerOwnershipUseCase(uow)

    with pytest.raises(ServerNotFoundError):
        await use_case(
            server_id=uuid4(),
            current_user_id=uuid4(),
            new_owner_id=uuid4(),
        )


async def test_rejects_transfer_to_self() -> None:
    uow, servers, members = _seeded_uow()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    use_case = TransferServerOwnershipUseCase(uow)

    with pytest.raises(CannotTransferToSelfError):
        await use_case(
            server_id=server.id,
            current_user_id=owner_id,
            new_owner_id=owner_id,
        )


async def test_rejects_non_owner() -> None:
    uow, servers, members = _seeded_uow()
    owner_id, member_id, other_id = uuid4(), uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=member_id, role=ServerMemberRole.member
        )
    )
    use_case = TransferServerOwnershipUseCase(uow)

    with pytest.raises(YouAreNotOwnerError):
        await use_case(
            server_id=server.id,
            current_user_id=member_id,
            new_owner_id=other_id,
        )


async def test_rejects_unknown_new_owner() -> None:
    uow, servers, members = _seeded_uow()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    use_case = TransferServerOwnershipUseCase(uow)

    with pytest.raises(MemberNotFoundError):
        await use_case(
            server_id=server.id,
            current_user_id=owner_id,
            new_owner_id=uuid4(),
        )


async def test_transfers_ownership_and_swaps_roles() -> None:
    uow, servers, members = _seeded_uow()
    owner_id, new_owner_id = uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=new_owner_id, role=ServerMemberRole.member
        )
    )
    use_case = TransferServerOwnershipUseCase(uow)

    updated = await use_case(
        server_id=server.id,
        current_user_id=owner_id,
        new_owner_id=new_owner_id,
    )

    assert updated.owner_id == new_owner_id

    roles = {m.user_id: m.role for m in members.members.values()}
    assert roles[owner_id] == ServerMemberRole.member
    assert roles[new_owner_id] == ServerMemberRole.owner
