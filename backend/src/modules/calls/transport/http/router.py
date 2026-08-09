from fastapi import APIRouter

from src.api.v1.dependencies import UserIdDep
from src.modules.calls.application.turn_credentials import build_ice_servers
from src.modules.calls.transport.http.schemas import (
    IceServerResponse,
    TurnCredentialsResponse,
)

router = APIRouter(prefix="/calls", tags=["Calls"])


@router.get("/turn-credentials", response_model=TurnCredentialsResponse)
async def get_turn_credentials(current_user_id: UserIdDep) -> TurnCredentialsResponse:
    ice_servers = build_ice_servers(current_user_id)
    return TurnCredentialsResponse(
        ice_servers=[IceServerResponse.model_validate(server) for server in ice_servers]
    )
