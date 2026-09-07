from uuid import UUID

from fastapi import APIRouter, status

from src.api.v1.dependencies import UserIdDep
from src.modules.channels.domain.entities.dtos import ChannelUpdateData
from src.modules.channels.transport.http.dependencies import (
    CreateChannelUseCaseDep,
    DeleteChannelUseCaseDep,
    GetChannelByIDUseCaseDep,
    GetChannelsUseCaseDep,
    UpdateChannelUseCaseDep,
)
from src.modules.channels.transport.http.schemas import (
    ChannelCreateRequest,
    ChannelResponse,
    ChannelUpdateRequest,
)
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/servers", tags=["Channels"])


@router.post(
    "/{server_id}/channels",
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    user_id: UserIdDep,
    server_id: UUID,
    use_case: CreateChannelUseCaseDep,
    data: ChannelCreateRequest,
) -> ChannelResponse:
    channel = await use_case(
        user_id=user_id,
        server_id=server_id,
        name=data.name,
        channel_type=data.type,
        topic=data.topic,
        is_private=data.is_private,
    )
    return ChannelResponse.model_validate(channel)


@router.get(
    "/{server_id}/channels",
    status_code=status.HTTP_200_OK,
    summary="Get all channels",
)
async def get_channels(
    user_id: UserIdDep,
    server_id: UUID,
    use_case: GetChannelsUseCaseDep,
) -> list[ChannelResponse]:
    channels = await use_case(user_id=user_id, server_id=server_id)
    return [ChannelResponse.model_validate(ch) for ch in channels]


@router.get(
    "/{server_id}/channels/{channel_id}",
    status_code=status.HTTP_200_OK,
    summary="Get channel by id",
)
async def get_channel(
    user_id: UserIdDep,
    server_id: UUID,
    channel_id: UUID,
    use_case: GetChannelByIDUseCaseDep,
) -> ChannelResponse:
    channel = await use_case(
        user_id=user_id,
        channel_id=channel_id,
        server_id=server_id,
    )
    return ChannelResponse.model_validate(channel)


@router.patch("/{server_id}/channels/{channel_id}", status_code=status.HTTP_200_OK)
async def update_channel(
    user_id: UserIdDep,
    server_id: UUID,
    channel_id: UUID,
    use_case: UpdateChannelUseCaseDep,
    data: ChannelUpdateRequest,
) -> ChannelResponse:
    channel = await use_case(
        channel_id=channel_id,
        user_id=user_id,
        server_id=server_id,
        update_data=unsettable_from_request(data, ChannelUpdateData),
    )
    return ChannelResponse.model_validate(channel)


@router.delete(
    "/{server_id}/channels/{channel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_channel(
    user_id: UserIdDep,
    server_id: UUID,
    channel_id: UUID,
    use_case: DeleteChannelUseCaseDep,
) -> None:
    await use_case(
        channel_id=channel_id,
        user_id=user_id,
        server_id=server_id,
    )
