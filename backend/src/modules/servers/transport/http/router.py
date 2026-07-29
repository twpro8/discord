from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import MediatorDep
from src.modules.servers.application.commands.create_server import CreateServerCommand
from src.modules.servers.application.commands.delete_server import DeleteServerCommand
from src.modules.servers.application.commands.join_server import JoinServerCommand
from src.modules.servers.application.commands.transfer_ownership import (
    TransferServerOwnershipCommand,
)
from src.modules.servers.application.commands.update_server import UpdateServerCommand
from src.modules.servers.application.queries.get_server_where_user_member import (
    GetServerWhereUserMemberQuery,
)
from src.modules.servers.application.queries.get_servers_where_user_member import (
    GetServersWhereUserMemberQuery,
)
from src.modules.servers.domain.entities.server import (
    ServerCreateRequest,
    ServerInviteCode,
    ServerResponse,
    ServerUpdateRequest,
    ServerUserSummary,
    UpdateOwnerID,
)
from src.modules.servers.domain.entities.server_member import ServerMemberResponse
from src.modules.servers.transport.http.invites import router as invite_router
from src.modules.users.transport.http.dependencies import UserIdDep
from src.shared.errors import LumiereError
from src.shared.result import Result

router = APIRouter(prefix="/servers", tags=["Servers"])
router.include_router(invite_router, prefix="/{server_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_server(
    current_user_id: UserIdDep,
    server_data: ServerCreateRequest,
    mediator: MediatorDep,
) -> ServerResponse:
    result = await mediator.send(
        CreateServerCommand(server_data=server_data, owner_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return ServerResponse.model_validate(result.value)


@router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_server(
    current_user_id: UserIdDep,
    code: ServerInviteCode,
    mediator: MediatorDep,
) -> ServerMemberResponse:
    result = await mediator.send(
        JoinServerCommand(user_id=current_user_id, code_schema=code)
    )
    if result.is_err:
        raise result.error
    return ServerMemberResponse.model_validate(result.value)


@router.post("/{server_id}/transfer", status_code=status.HTTP_200_OK)
async def transfer_ownership(
    server_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    owner_id: UpdateOwnerID,
) -> ServerResponse:
    result = await mediator.send(
        TransferServerOwnershipCommand(
            server_id=server_id,
            current_user_id=current_user_id,
            data=owner_id,
        )
    )
    if result.is_err:
        raise result.error
    return ServerResponse.model_validate(result.value)


@router.get("", response_model=list[ServerUserSummary])
async def get_my_servers(
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> list[ServerUserSummary]:
    result: Result[list[ServerUserSummary], LumiereError] = await mediator.query(
        GetServersWhereUserMemberQuery(user_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return result.value


@router.get("/{server_id}", response_model=ServerResponse)
async def get_my_server(
    current_user_id: UserIdDep,
    server_id: UUID,
    mediator: MediatorDep,
) -> ServerResponse:
    result = await mediator.query(
        GetServerWhereUserMemberQuery(user_id=current_user_id, server_id=server_id)
    )
    if result.is_err:
        raise result.error
    return ServerResponse.model_validate(result.value)


@router.patch("/{server_id}")
async def update_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    update_data: ServerUpdateRequest,
    mediator: MediatorDep,
) -> ServerResponse:
    result = await mediator.send(
        UpdateServerCommand(
            update_data=update_data,
            server_id=server_id,
            owner_id=current_user_id,
        )
    )
    if result.is_err:
        raise result.error
    return ServerResponse.model_validate(result.value)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteServerCommand(server_id=server_id, owner_id=current_user_id)
    )
    if result.is_err:
        raise result.error
