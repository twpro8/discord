from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import UserIdDep
from src.modules.channels.domain.entities.dtos import ChannelUpdateData
from src.modules.channels.transport.http.dependencies import (
    DeleteChannelUseCaseDep,
    UpdateChannelUseCaseDep,
)
from src.modules.channels.transport.http.schemas import (
    ChannelResponse,
    ChannelUpdateRequest,
)
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/servers", tags=["Channels"])


@router.patch("/{server_id}/channels/{channel_id}", status_code=status.HTTP_200_OK)
async def update_channel(
    server_id: UUID,
    channel_id: UUID,
    current_user_id: UserIdDep,
    update_data: ChannelUpdateRequest,
    use_case: UpdateChannelUseCaseDep,
) -> ChannelResponse:
    channel = await use_case(
        channel_id=channel_id,
        user_id=current_user_id,
        server_id=server_id,
        update_data=unsettable_from_request(update_data, ChannelUpdateData),
    )
    return ChannelResponse.model_validate(channel)


@router.delete(
    "/{server_id}/channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_channel(
    server_id: UUID,
    channel_id: UUID,
    current_user_id: UserIdDep,
    use_case: DeleteChannelUseCaseDep,
) -> None:
    await use_case(
        channel_id=channel_id,
        user_id=current_user_id,
        server_id=server_id,
    )
