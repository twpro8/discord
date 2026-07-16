from uuid import UUID

from fastapi import APIRouter, status

from src.server.dependencies import ServerMemberServiceDep, ServerServiceDep
from src.server.schemas import (
    ServerCreateRequestSchema,
    ServerInviteCode,
    ServerSchema,
    ServerUpdateRequestSchema,
    ServerUserBriefSchema,
    UpdateOwnerIdSchema,
)
from src.server.server_member.schemas import ServerMemberSchema
from src.user.dependencies import UserIdDep
from src.server.invite.router import router as invite_router

router = APIRouter(prefix="/servers", tags=["Servers"])
router.include_router(invite_router, prefix="/{server_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_server(
    current_user_id: UserIdDep,
    server_data: ServerCreateRequestSchema,
    service: ServerServiceDep,
) -> ServerSchema:
    new_server = await service.create_server(
        server_data=server_data,
        owner_id=current_user_id,
    )
    return new_server


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_server(
    current_user_id: UserIdDep,
    code: ServerInviteCode,
    service: ServerMemberServiceDep,
) -> ServerMemberSchema:
    new_server = await service.join_server(user_id=current_user_id, code_schema=code)
    return new_server


@router.post("/{server_id}/transfer", status_code=status.HTTP_200_OK)
async def transfer_ownership(
    server_id: UUID,
    current_user_id: UserIdDep,
    service: ServerServiceDep,
    owner_id: UpdateOwnerIdSchema,
) -> ServerSchema:
    new_server = await service.transfer_server_ownership(
        server_id=server_id, current_user_id=current_user_id, data=owner_id
    )
    return new_server


@router.get("", response_model=list[ServerUserBriefSchema])
async def get_my_servers(
    current_user_id: UserIdDep,
    service: ServerServiceDep,
) -> list[ServerUserBriefSchema]:
    return await service.get_servers_where_user_memeber(user_id=current_user_id)


@router.get("/{server_id}", response_model=ServerSchema)
async def get_my_server(
    current_user_id: UserIdDep,
    server_id: UUID,
    service: ServerServiceDep,
) -> ServerSchema | None:
    return await service.get_server_where_user_member(
        user_id=current_user_id, server_id=server_id
    )


@router.patch("/{server_id}")
async def update_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    update_data: ServerUpdateRequestSchema,
    service: ServerServiceDep,
) -> ServerSchema:
    updated_server = await service.update_server(
        update_data=update_data,
        server_id=server_id,
        owner_id=current_user_id,
    )
    return updated_server


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    service: ServerServiceDep,
) -> None:
    await service.delete_server(
        server_id=server_id,
        owner_id=current_user_id,
    )
