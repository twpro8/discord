from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import UserIdDep
from src.modules.servers.domain.entities.dtos import ServerCreateData, ServerUpdateData
from src.modules.servers.transport.http.dependencies import (
    CreateServerUseCaseDep,
    DeleteServerUseCaseDep,
    GetServerMembersUseCaseDep,
    GetServersWhereUserMemberUseCaseDep,
    GetServerWhereUserMemberUseCaseDep,
    JoinServerUseCaseDep,
    TransferServerOwnershipUseCaseDep,
    UpdateServerUseCaseDep,
)
from src.modules.servers.transport.http.invites import router as invite_router
from src.modules.servers.transport.http.schemas import (
    ServerCreateRequest,
    ServerInviteCode,
    ServerMemberResponse,
    ServerMemberWithUserResponse,
    ServerResponse,
    ServerUpdateRequest,
    ServerUserSummaryResponse,
    UpdateOwnerID,
)
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/servers", tags=["Servers"])
router.include_router(invite_router, prefix="/{server_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_server(
    current_user_id: UserIdDep,
    server_data: ServerCreateRequest,
    use_case: CreateServerUseCaseDep,
) -> ServerResponse:
    server = await use_case(
        server_data=ServerCreateData(**server_data.model_dump()),
        owner_id=current_user_id,
    )
    return ServerResponse.model_validate(server)


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_server(
    current_user_id: UserIdDep,
    code: ServerInviteCode,
    use_case: JoinServerUseCaseDep,
) -> ServerMemberResponse:
    member = await use_case(user_id=current_user_id, code=code.code)
    return ServerMemberResponse.model_validate(member)


@router.post("/{server_id}/transfer", status_code=status.HTTP_200_OK)
async def transfer_ownership(
    server_id: UUID,
    current_user_id: UserIdDep,
    use_case: TransferServerOwnershipUseCaseDep,
    owner_id: UpdateOwnerID,
) -> ServerResponse:
    server = await use_case(
        server_id=server_id,
        current_user_id=current_user_id,
        new_owner_id=owner_id.owner_id,
    )
    return ServerResponse.model_validate(server)


@router.get("", response_model=list[ServerUserSummaryResponse])
async def get_my_servers(
    current_user_id: UserIdDep,
    use_case: GetServersWhereUserMemberUseCaseDep,
) -> list[ServerUserSummaryResponse]:
    servers = await use_case(user_id=current_user_id)
    return [ServerUserSummaryResponse.model_validate(s) for s in servers]


@router.get("/{server_id}", response_model=ServerResponse)
async def get_my_server(
    current_user_id: UserIdDep,
    server_id: UUID,
    use_case: GetServerWhereUserMemberUseCaseDep,
) -> ServerResponse:
    server = await use_case(user_id=current_user_id, server_id=server_id)
    return ServerResponse.model_validate(server)


@router.get("/{server_id}/members", response_model=list[ServerMemberWithUserResponse])
async def get_server_members(
    server_id: UUID,
    current_user_id: UserIdDep,
    use_case: GetServerMembersUseCaseDep,
) -> list[ServerMemberWithUserResponse]:
    members = await use_case(server_id=server_id, requesting_user_id=current_user_id)
    return [ServerMemberWithUserResponse.model_validate(m) for m in members]


@router.patch("/{server_id}")
async def update_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    update_data: ServerUpdateRequest,
    use_case: UpdateServerUseCaseDep,
) -> ServerResponse:
    server = await use_case(
        update_data=unsettable_from_request(update_data, ServerUpdateData),
        server_id=server_id,
        owner_id=current_user_id,
    )
    return ServerResponse.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    use_case: DeleteServerUseCaseDep,
) -> None:
    await use_case(server_id=server_id, owner_id=current_user_id)
