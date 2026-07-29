from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import MediatorDep
from src.modules.servers.application.commands.create_invite import CreateInviteCommand
from src.modules.servers.application.commands.delete_invite import DeleteInviteCommand
from src.modules.servers.application.queries.get_invites import GetInvitesQuery
from src.modules.servers.domain.entities.server_invite import (
    ServerInviteCreateRequest,
    ServerInviteResponse,
    ServerInviteWithStatus,
)
from src.modules.users.transport.http.dependencies import UserIdDep
from src.shared.errors import LumiereError
from src.shared.result import Result

router = APIRouter(prefix="/invites", tags=["Server Invites"])


@router.post(
    "", response_model=ServerInviteResponse, status_code=status.HTTP_201_CREATED
)
async def create_invite(
    server_id: UUID,
    current_user_id: UserIdDep,
    payload: ServerInviteCreateRequest,
    mediator: MediatorDep,
) -> ServerInviteResponse:
    result = await mediator.send(
        CreateInviteCommand(
            server_id=server_id,
            user_id=current_user_id,
            payload=payload,
        )
    )
    if result.is_err:
        raise result.error
    return ServerInviteResponse.model_validate(result.value)


@router.get("", response_model=list[ServerInviteWithStatus])
async def get_invites(
    user_id: UserIdDep,
    server_id: UUID,
    mediator: MediatorDep,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[ServerInviteWithStatus]:
    result: Result[list[ServerInviteWithStatus], LumiereError] = await mediator.query(
        GetInvitesQuery(
            user_id=user_id,
            server_id=server_id,
            limit=limit,
            offset=offset,
        )
    )
    if result.is_err:
        raise result.error
    return result.value


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invite(
    server_id: UUID,
    code: str,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteInviteCommand(
            server_id=server_id,
            user_id=current_user_id,
            code=code,
        )
    )
    if result.is_err:
        raise result.error
