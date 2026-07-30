from uuid import UUID

from fastapi import APIRouter

from src.api.v1.dependencies import MediatorDep
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
)
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
)
from src.modules.messages.domain.entities.schemas import (
    ChannelMessage,
    ChatMessage,
    MessageCreateRequest,
)
from src.modules.users.transport.http.dependencies import UserIdDep
from src.shared.errors import LumiereError
from src.shared.result import Result

channel_message_router = APIRouter(prefix="/messages", tags=["Channel Messages"])
chat_message_router = APIRouter(prefix="/messages", tags=["Chat Messages"])


@channel_message_router.post("")
async def send_channel_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    mediator: MediatorDep,
    channel_id: UUID,
) -> ChannelMessage:
    result: Result[ChannelMessage, LumiereError] = await mediator.send(
        SendChannelMessageCommand(
            channel_id=channel_id,
            sender_id=user_id,
            data=data,
        )
    )
    if result.is_err:
        raise result.error
    return result.value


@chat_message_router.post("")
async def send_chat_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    mediator: MediatorDep,
    chat_id: UUID,
) -> ChatMessage:
    result: Result[ChatMessage, LumiereError] = await mediator.send(
        SendChatMessageCommand(
            chat_id=chat_id,
            sender_id=user_id,
            data=data,
        )
    )
    if result.is_err:
        raise result.error
    return result.value
