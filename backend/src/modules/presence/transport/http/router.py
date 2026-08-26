from uuid import UUID

from fastapi import APIRouter

from src.api.v1.dependencies import UserIdDep
from src.modules.presence.transport.http.dependencies import (
    GetFriendsPresenceUseCaseDep,
    GetServerPresenceUseCaseDep,
)
from src.modules.presence.transport.http.schemas import PresenceResponse

router = APIRouter(prefix="/presence", tags=["Presence"])


@router.get("/friends", response_model=list[PresenceResponse])
async def get_friends_presence(
    current_user_id: UserIdDep,
    use_case: GetFriendsPresenceUseCaseDep,
) -> list[PresenceResponse]:
    statuses = await use_case(user_id=current_user_id)
    return [PresenceResponse.model_validate(dto) for dto in statuses]


@router.get("/servers/{server_id}", response_model=list[PresenceResponse])
async def get_server_presence(
    server_id: UUID,
    current_user_id: UserIdDep,
    use_case: GetServerPresenceUseCaseDep,
) -> list[PresenceResponse]:
    statuses = await use_case(server_id=server_id, requesting_user_id=current_user_id)
    return [PresenceResponse.model_validate(dto) for dto in statuses]
