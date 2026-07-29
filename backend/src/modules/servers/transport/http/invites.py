from uuid import UUID

from fastapi import APIRouter, Query, status

from src.modules.servers.domain.entities.server_invite import (
    ServerInviteCreateRequest,
    ServerInviteResponse,
    ServerInviteWithStatus,
)
from src.modules.servers.transport.http.dependencies import (
    CreateInviteCommandDep,
    DeleteInviteCommandDep,
    GetInvitesQueryDep,
)
from src.modules.users.transport.http.dependencies import UserIdDep

router = APIRouter(prefix="/invites", tags=["Server Invites"])


@router.post(
    "", response_model=ServerInviteResponse, status_code=status.HTTP_201_CREATED
)
async def create_invite(
    server_id: UUID,
    current_user_id: UserIdDep,
    payload: ServerInviteCreateRequest,
    command: CreateInviteCommandDep,
) -> ServerInviteResponse:
    invite = await command(
        server_id=server_id,
        user_id=current_user_id,
        payload=payload,
    )
    return ServerInviteResponse.model_validate(invite)


@router.get("", response_model=list[ServerInviteWithStatus])
async def get_invites(
    user_id: UserIdDep,
    server_id: UUID,
    query: GetInvitesQueryDep,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServerInviteWithStatus]:
    return await query(
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
    command: DeleteInviteCommandDep,
) -> None:
    await command(
        server_id=server_id,
        user_id=current_user_id,
        code=code,
    )
