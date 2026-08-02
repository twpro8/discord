from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.chats.application.commands.mark_chat_as_read import (
    MarkChatAsReadCommand,
)
from src.modules.messages.application.commands.delete_message import (
    DeleteMessageCommand,
)
from src.modules.messages.application.commands.edit_message import EditMessageCommand
from src.modules.messages.application.commands.send_channel_message import (
    SendChannelMessageCommand,
)
from src.modules.messages.application.commands.send_chat_message import (
    SendChatMessageCommand,
)
from src.modules.messages.application.queries.list_channel_messages import (
    ListChannelMessagesQuery,
)
from src.modules.messages.application.queries.list_chat_messages import (
    ListChatMessagesQuery,
)
from src.modules.messages.domain.entities.dtos import (
    ChannelMessage,
    ChannelMessagePage,
    ChatMessage,
    ChatMessagePage,
    MessageCreateData,
    MessageEditData,
)
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.transport.http.schemas import (
    ChannelMessagePageResponse,
    ChannelMessageResponse,
    ChatMessagePageResponse,
    ChatMessageResponse,
    MessageCreateRequest,
    MessageEditRequest,
)
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
) -> ChannelMessageResponse:
    result: Result[ChannelMessage, LumiereError] = await mediator.send(
        SendChannelMessageCommand(
            channel_id=channel_id,
            sender_id=user_id,
            data=MessageCreateData(**data.model_dump()),
        )
    )
    if result.is_err:
        raise result.error
    return ChannelMessageResponse.model_validate(result.value)


@chat_message_router.post("")
async def send_chat_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    mediator: MediatorDep,
    chat_id: UUID,
) -> ChatMessageResponse:
    result: Result[ChatMessage, LumiereError] = await mediator.send(
        SendChatMessageCommand(
            chat_id=chat_id,
            sender_id=user_id,
            data=MessageCreateData(**data.model_dump()),
        )
    )
    if result.is_err:
        raise result.error
    return ChatMessageResponse.model_validate(result.value)


@channel_message_router.get("")
async def list_channel_messages(
    channel_id: UUID,
    user_id: UserIdDep,
    mediator: MediatorDep,
    limit: int = Query(20, gt=0, le=100),
    before_cursor: str | None = Query(None, max_length=128),
    after_cursor: str | None = Query(None, max_length=128),
) -> ChannelMessagePageResponse:
    result: Result[ChannelMessagePage, LumiereError] = await mediator.query(
        ListChannelMessagesQuery(
            channel_id=channel_id,
            user_id=user_id,
            limit=limit,
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )
    )
    if result.is_err:
        raise result.error
    return ChannelMessagePageResponse.model_validate(result.value)


@chat_message_router.get("")
async def list_chat_messages(
    chat_id: UUID,
    user_id: UserIdDep,
    mediator: MediatorDep,
    limit: int = Query(20, gt=0, le=100),
    before_cursor: str | None = Query(None, max_length=128),
    after_cursor: str | None = Query(None, max_length=128),
) -> ChatMessagePageResponse:
    result: Result[ChatMessagePage, LumiereError] = await mediator.query(
        ListChatMessagesQuery(
            chat_id=chat_id,
            user_id=user_id,
            limit=limit,
            before_cursor=before_cursor,
            after_cursor=after_cursor,
        )
    )
    if result.is_err:
        raise result.error

    page = result.value
    if page.items:
        # listing a chat's messages auto-advances the caller's
        # last-read cursor. Reuses chats' own mark-as-read command (best
        # effort — a failure here shouldn't fail the read the user asked
        # for) instead of adding new cross-module write plumbing.
        max_seq = max(m.sequence for m in page.items)
        mark_read_result = await mediator.send(
            MarkChatAsReadCommand(
                chat_id=chat_id, user_id=user_id, up_to_sequence=max_seq
            )
        )
        if mark_read_result.is_err:
            raise mark_read_result.error

    return ChatMessagePageResponse.model_validate(page)


@channel_message_router.patch("/{message_id}")
async def edit_channel_message(
    channel_id: UUID,
    message_id: UUID,
    data: MessageEditRequest,
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> ChannelMessageResponse:
    result: Result[Message, LumiereError] = await mediator.send(
        EditMessageCommand(
            message_id=message_id,
            sender_id=user_id,
            data=MessageEditData(**data.model_dump()),
            channel_id=channel_id,
        )
    )
    if result.is_err:
        raise result.error
    return ChannelMessageResponse.model_validate(result.value)


@chat_message_router.patch("/{message_id}")
async def edit_chat_message(
    chat_id: UUID,
    message_id: UUID,
    data: MessageEditRequest,
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> ChatMessageResponse:
    result: Result[Message, LumiereError] = await mediator.send(
        EditMessageCommand(
            message_id=message_id,
            sender_id=user_id,
            data=MessageEditData(**data.model_dump()),
            chat_id=chat_id,
        )
    )
    if result.is_err:
        raise result.error
    return ChatMessageResponse.model_validate(result.value)


@channel_message_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel_message(
    channel_id: UUID,
    message_id: UUID,
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteMessageCommand(
            message_id=message_id, user_id=user_id, channel_id=channel_id
        )
    )
    if result.is_err:
        raise result.error


@chat_message_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    chat_id: UUID,
    message_id: UUID,
    user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        DeleteMessageCommand(message_id=message_id, user_id=user_id, chat_id=chat_id)
    )
    if result.is_err:
        raise result.error
