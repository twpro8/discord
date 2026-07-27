from uuid import UUID

from fastapi import APIRouter

from src.modules.messages.dependencies import MessageServiceDep
from src.modules.messages.schemas import (
    ChannelMessage,
    ChatMessage,
    MessageCreateRequest,
)
from src.modules.users.transport.http.dependencies import UserIdDep

channel_message_router = APIRouter(prefix="/messages", tags=["Channel Messages"])
chat_message_router = APIRouter(prefix="/messages", tags=["Chat Messages"])


@channel_message_router.post("")
async def send_channel_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    service: MessageServiceDep,
    channel_id: UUID,
) -> ChannelMessage:
    return await service.send_channel_message(
        channel_id=channel_id,
        sender_id=user_id,
        data=data,
    )


@chat_message_router.post("")
async def send_chat_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    service: MessageServiceDep,
    chat_id: UUID,
) -> ChatMessage:
    return await service.send_chat_message(
        chat_id=chat_id,
        sender_id=user_id,
        data=data,
    )
