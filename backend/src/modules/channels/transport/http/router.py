from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import UserIdDep
from src.modules.channels.domain.entities.dtos import ChannelUpdateData
from src.modules.channels.transport.http.dependencies import (
    DeleteChannelUseCaseDep,
    UpdateChannelUseCaseDep,
)
from src.modules.channels.transport.http.schemas import (
    ChannelDeleteRequest,
    ChannelResponse,
    ChannelUpdateRequest,
)
from src.modules.messages.transport.http.router import channel_message_router
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/channels", tags=["Channels"])
router.include_router(channel_message_router, prefix="/{channel_id}")


@router.patch("/{channel_id}", status_code=status.HTTP_200_OK)
async def update_channel(
    channel_id: UUID,
    current_user_id: UserIdDep,
    update_data: ChannelUpdateRequest,
    use_case: UpdateChannelUseCaseDep,
) -> ChannelResponse:
    channel = await use_case(
        channel_id=channel_id,
        user_id=current_user_id,
        server_id=update_data.server_id,
        update_data=unsettable_from_request(update_data, ChannelUpdateData),
    )
    return ChannelResponse.model_validate(channel)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: UUID,
    current_user_id: UserIdDep,
    delete_data: ChannelDeleteRequest,
    use_case: DeleteChannelUseCaseDep,
) -> None:
    await use_case(
        channel_id=channel_id,
        user_id=current_user_id,
        server_id=delete_data.server_id,
    )
