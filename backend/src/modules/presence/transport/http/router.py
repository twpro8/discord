from uuid import UUID

from fastapi import APIRouter

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.presence.application.queries.get_friends_presence import (
    GetFriendsPresenceQuery,
)
from src.modules.presence.application.queries.get_server_presence import (
    GetServerPresenceQuery,
)
from src.modules.presence.domain.entities.dtos import PresenceDTO
from src.modules.presence.transport.http.schemas import PresenceResponse
from src.shared.errors import LumiereError
from src.shared.result import Result

router = APIRouter(prefix="/presence", tags=["Presence"])


@router.get("/friends", response_model=list[PresenceResponse])
async def get_friends_presence(
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> list[PresenceResponse]:
    result: Result[list[PresenceDTO], LumiereError] = await mediator.query(
        GetFriendsPresenceQuery(user_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return [PresenceResponse.model_validate(dto) for dto in result.value]


@router.get("/servers/{server_id}", response_model=list[PresenceResponse])
async def get_server_presence(
    server_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> list[PresenceResponse]:
    result: Result[list[PresenceDTO], LumiereError] = await mediator.query(
        GetServerPresenceQuery(server_id=server_id, requesting_user_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return [PresenceResponse.model_validate(dto) for dto in result.value]
