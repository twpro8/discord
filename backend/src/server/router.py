from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.server.dependencies import ServerServiceDep
from src.server.exceptions import ServerNotEmptyError, ServerNotFoundError
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


@router.get("/{server_id}", response_model=ServerSchema)
async def get_my_server(
    current_user_id: UserIdDep,
    server_id: UUID,
    service: ServerServiceDep,
) -> ServerSchema | None:
    return await service.get_server_where_user_member(
        user_id=current_user_id, server_id=server_id
    )


@router.patch("/update/{server_id}")
async def update_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    update_data: ServerUpdateRequestSchema,
    service: ServerServiceDep,
) -> ServerSchema:
    try:
        updated_server = await service.update_server(
            update_data=update_data,
            server_id=server_id,
            owner_id=current_user_id,
        )
    except ServerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server does not exist",
        )
    return updated_server


@router.delete("/delete/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    service: ServerServiceDep,
) -> None:
    try:
        await service.delete_server(
            server_id=server_id,
            owner_id=current_user_id,
        )
    except ServerNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Server does not exist",
        )
    except ServerNotEmptyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Server has to be empty",
        )
