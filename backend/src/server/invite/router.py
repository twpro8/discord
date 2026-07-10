from uuid import UUID

from fastapi import APIRouter, Query, status
from src.server.dependencies import ServerInviteServiceDep
from src.server.invite.schemas import (
    CreateServerInviteRequestSchema,
    ServerInviteSchema,
    ServerInviteWithStatusSchema,
)
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/{server_id}/invites", tags=["Server Invites"])


@router.post("", response_model=ServerInviteSchema, status_code=status.HTTP_201_CREATED)
async def create_invite(
    server_id: UUID,
    current_user_id: UserIdDep,
    payload: CreateServerInviteRequestSchema,
    service: ServerInviteServiceDep,
) -> ServerInviteSchema:
    return await service.create_invite(
        server_id=server_id, user_id=current_user_id, payload=payload
    )


@router.get("", response_model=list[ServerInviteWithStatusSchema])
async def list_invites(
    server_id: UUID,
    service: ServerInviteServiceDep,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServerInviteWithStatusSchema]:
    return await service.list_invites(server_id=server_id, limit=limit, offset=offset)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(
    server_id: UUID,
    code: str,
    current_user_id: UserIdDep,
    service: ServerInviteServiceDep,
) -> None:
    await service.delete_invite(server_id=server_id, user_id=current_user_id, code=code)
