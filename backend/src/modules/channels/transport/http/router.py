from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.channels.application.commands.delete_channel import (
    DeleteChannelCommand,
)
from src.modules.channels.application.commands.update_channel import (
    UpdateChannelCommand,
)
from src.modules.channels.domain.entities.channel import Channel
from src.modules.channels.domain.entities.dtos import ChannelUpdateData
from src.modules.channels.transport.http.schemas import (
    ChannelDeleteRequest,
    ChannelResponse,
    ChannelUpdateRequest,
)
from src.modules.messages.module import get_channel_message_router
from src.shared.errors import LumiereError
from src.shared.result import Result
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/channels", tags=["Channels"])
router.include_router(get_channel_message_router(), prefix="/{channel_id}")


@router.patch("/{channel_id}", status_code=status.HTTP_200_OK)
async def update_channel(
    channel_id: UUID,
    current_user_id: UserIdDep,
    update_data: ChannelUpdateRequest,
    mediator: MediatorDep,
) -> ChannelResponse:
    result: Result[Channel, LumiereError] = await mediator.send(
        UpdateChannelCommand(
            channel_id=channel_id,
            user_id=current_user_id,
            server_id=update_data.server_id,
            update_data=unsettable_from_request(update_data, ChannelUpdateData),
        )
    )
    if result.is_err:
        raise result.error
    return ChannelResponse.model_validate(result.value)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: UUID,
    current_user_id: UserIdDep,
    delete_data: ChannelDeleteRequest,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteChannelCommand(
            channel_id=channel_id,
            user_id=current_user_id,
            server_id=delete_data.server_id,
        )
    )
    if result.is_err:
        raise result.error
