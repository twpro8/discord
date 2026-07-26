from uuid import UUID

from fastapi import APIRouter, Query, status

from src.modules.server.dependencies import ServerInviteServiceDep
from src.modules.server.invite.schemas import (
    CreateServerInviteRequest,
    ServerInvite,
    ServerInviteWithStatus,
)
from src.modules.user.dependencies import UserIdDep

router = APIRouter(prefix="/invites", tags=["Server Invites"])


@router.post("", response_model=ServerInvite, status_code=status.HTTP_201_CREATED)
async def create_invite(
    server_id: UUID,
    current_user_id: UserIdDep,
    payload: CreateServerInviteRequest,
    service: ServerInviteServiceDep,
) -> ServerInvite:
    return await service.create_invite(
        server_id=server_id,
        user_id=current_user_id,
        payload=payload,
    )


@router.get("", response_model=list[ServerInviteWithStatus])
async def get_invites(
    user_id: UserIdDep,
    server_id: UUID,
    service: ServerInviteServiceDep,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServerInviteWithStatus]:
    return await service.list_invites(
        user_id=user_id,
        server_id=server_id,
        limit=limit,
        offset=offset,
    )


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(
    server_id: UUID,
    code: str,
    current_user_id: UserIdDep,
    service: ServerInviteServiceDep,
) -> None:
    await service.delete_invite(
        server_id=server_id,
        user_id=current_user_id,
        code=code,
    )
