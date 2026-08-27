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
from tests.unit.servers.fakes import FakeServerMemberRepository, FakeServerRepository


def _seeded_repos() -> tuple[FakeServerRepository, FakeServerMemberRepository]:
    return FakeServerRepository(), FakeServerMemberRepository()


async def test_rejects_unknown_server() -> None:
    servers, members = _seeded_repos()
    use_case = TransferServerOwnershipUseCase(servers, members)

    with pytest.raises(ServerNotFoundError):
        await use_case(
            server_id=uuid4(),
            current_user_id=uuid4(),
            new_owner_id=uuid4(),
        )


async def test_rejects_transfer_to_self() -> None:
    servers, members = _seeded_repos()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    use_case = TransferServerOwnershipUseCase(servers, members)

    with pytest.raises(CannotTransferToSelfError):
        await use_case(
            server_id=server.id,
            current_user_id=owner_id,
            new_owner_id=owner_id,
        )


async def test_rejects_non_owner() -> None:
    servers, members = _seeded_repos()
    owner_id, member_id, other_id = uuid4(), uuid4(), uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=member_id, role=ServerMemberRole.member
        )
    )
    use_case = TransferServerOwnershipUseCase(servers, members)

    with pytest.raises(YouAreNotOwnerError):
        await use_case(
            server_id=server.id,
            current_user_id=member_id,
            new_owner_id=other_id,
        )


async def test_rejects_unknown_new_owner() -> None:
    servers, members = _seeded_repos()
    owner_id = uuid4()
    server = await servers.create(ServerCreate(name="S", owner_id=owner_id))
    await members.create(
        ServerMemberCreate(
            server_id=server.id, user_id=owner_id, role=ServerMemberRole.owner
        )
    )
    use_case = TransferServerOwnershipUseCase(servers, members)

    with pytest.raises(MemberNotFoundError):
        await use_case(
            server_id=server.id,
            current_user_id=owner_id,
            new_owner_id=uuid4(),
        )


async def test_transfers_ownership_and_swaps_roles() -> None:
    servers, members = _seeded_repos()
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
    use_case = TransferServerOwnershipUseCase(servers, members)

    updated = await use_case(
        server_id=server.id,
        current_user_id=owner_id,
        new_owner_id=new_owner_id,
    )

    assert updated.owner_id == new_owner_id

    roles = {m.user_id: m.role for m in members.members.values()}
    assert roles[owner_id] == ServerMemberRole.member
    assert roles[new_owner_id] == ServerMemberRole.owner
