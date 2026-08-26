from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import UserIdDep
from src.modules.servers.domain.entities.dtos import ServerInviteCreateData
from src.modules.servers.transport.http.dependencies import (
    CreateInviteUseCaseDep,
    DeleteInviteUseCaseDep,
    GetInvitesUseCaseDep,
)
from src.modules.servers.transport.http.schemas import (
    ServerInviteCreateRequest,
    ServerInviteResponse,
    ServerInviteWithStatusResponse,
)

router = APIRouter(prefix="/invites", tags=["Server Invites"])


@router.post(
    "", response_model=ServerInviteResponse, status_code=status.HTTP_201_CREATED
)
async def create_invite(
    server_id: UUID,
    current_user_id: UserIdDep,
    payload: ServerInviteCreateRequest,
    use_case: CreateInviteUseCaseDep,
) -> ServerInviteResponse:
    invite = await use_case(
        server_id=server_id,
        user_id=current_user_id,
        payload=ServerInviteCreateData(**payload.model_dump()),
    )
    return ServerInviteResponse.model_validate(invite)


@router.get("", response_model=list[ServerInviteWithStatusResponse])
async def get_invites(
    user_id: UserIdDep,
    server_id: UUID,
    use_case: GetInvitesUseCaseDep,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServerInviteWithStatusResponse]:
    invites = await use_case(
        user_id=user_id,
        server_id=server_id,
        limit=limit,
        offset=offset,
    )
    return [ServerInviteWithStatusResponse.model_validate(i) for i in invites]


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(
    server_id: UUID,
    code: str,
    current_user_id: UserIdDep,
    use_case: DeleteInviteUseCaseDep,
) -> None:
    await use_case(
        server_id=server_id,
        user_id=current_user_id,
        code=code,
    )
