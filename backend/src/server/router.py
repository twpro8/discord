from uuid import UUID

from fastapi import APIRouter, status

from src.server.dependencies import ServerServiceDep
from src.server.schemas import (
    ServerCreateRequestSchema,
    ServerSchema,
    ServerUpdateRequestSchema,
    ServerUserBriefSchema,
)
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/servers", tags=["Servers"])


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


@router.get("", response_model=list[ServerUserBriefSchema])
async def get_my_servers(
    current_user_id: UserIdDep,
    service: ServerServiceDep,
) -> list[ServerUserBriefSchema]:
    return await service.get_servers_where_user_memeber(user_id=current_user_id)


@router.patch("/update/{server_id}")
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


@router.delete("/delete/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    service: ServerServiceDep,
) -> None:
    await service.delete_server(
        server_id=server_id,
        owner_id=current_user_id,
    )
