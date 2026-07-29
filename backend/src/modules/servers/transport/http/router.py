from uuid import UUID

from fastapi import APIRouter, status

from src.modules.servers.domain.entities.server import (
    ServerCreateRequest,
    ServerInviteCode,
    ServerResponse,
    ServerUpdateRequest,
    ServerUserSummary,
    UpdateOwnerID,
)
from src.modules.servers.domain.entities.server_member import ServerMemberResponse
from src.modules.servers.transport.http.dependencies import (
    CreateServerCommandDep,
    DeleteServerCommandDep,
    GetServersWhereUserMemberQueryDep,
    GetServerWhereUserMemberQueryDep,
    JoinServerCommandDep,
    TransferServerOwnershipCommandDep,
    UpdateServerCommandDep,
)
from src.modules.servers.transport.http.invites import router as invite_router
from src.modules.users.transport.http.dependencies import UserIdDep

router = APIRouter(prefix="/servers", tags=["Servers"])
router.include_router(invite_router, prefix="/{server_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_server(
    current_user_id: UserIdDep,
    server_data: ServerCreateRequest,
    command: CreateServerCommandDep,
) -> ServerResponse:
    new_server = await command(server_data=server_data, owner_id=current_user_id)
    return ServerResponse.model_validate(new_server)


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_server(
    current_user_id: UserIdDep,
    code: ServerInviteCode,
    command: JoinServerCommandDep,
) -> ServerMemberResponse:
    member = await command(user_id=current_user_id, code_schema=code)
    return ServerMemberResponse.model_validate(member)


@router.post("/{server_id}/transfer", status_code=status.HTTP_200_OK)
async def transfer_ownership(
    server_id: UUID,
    current_user_id: UserIdDep,
    command: TransferServerOwnershipCommandDep,
    owner_id: UpdateOwnerID,
) -> ServerResponse:
    new_server = await command(
        server_id=server_id,
        current_user_id=current_user_id,
        data=owner_id,
    )
    return ServerResponse.model_validate(new_server)


@router.get("", response_model=list[ServerUserSummary])
async def get_my_servers(
    current_user_id: UserIdDep,
    query: GetServersWhereUserMemberQueryDep,
) -> list[ServerUserSummary]:
    return await query(user_id=current_user_id)


@router.get("/{server_id}", response_model=ServerResponse)
async def get_my_server(
    current_user_id: UserIdDep,
    server_id: UUID,
    query: GetServerWhereUserMemberQueryDep,
) -> ServerResponse:
    server = await query(user_id=current_user_id, server_id=server_id)
    return ServerResponse.model_validate(server)


@router.patch("/{server_id}")
async def update_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    update_data: ServerUpdateRequest,
    command: UpdateServerCommandDep,
) -> ServerResponse:
    updated_server = await command(
        update_data=update_data,
        server_id=server_id,
        owner_id=current_user_id,
    )
    return ServerResponse.model_validate(updated_server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    command: DeleteServerCommandDep,
) -> None:
    await command(server_id=server_id, owner_id=current_user_id)
