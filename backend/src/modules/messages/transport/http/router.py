"""`messages` has no top-level router of its own, unlike the other 6 HTTP
modules: its HTTP surface is a sub-resource of chats/channels (POST
/chats/{chat_id}/messages, /channels/{channel_id}/messages), so
`api/v1/router.py` never mounts it directly — `chats`' and `channels`' own
routers import `chat_message_router`/`channel_message_router` from here and
pull them in via `router.include_router(..., prefix="/{chat_id}" |
"/{channel_id}")`. Use-case DI wiring is unaffected:
`messages/transport/http/dependencies.py` builds its own use cases the same
way every other module does."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import UserIdDep
from src.modules.chats.transport.http.dependencies import MarkChatAsReadUseCaseDep
from src.modules.messages.domain.entities.dtos import MessageCreateData, MessageEditData
from src.modules.messages.transport.http.dependencies import (
    DeleteMessageUseCaseDep,
    EditMessageUseCaseDep,
    ListChannelMessagesUseCaseDep,
    ListChatMessagesUseCaseDep,
    SendChannelMessageUseCaseDep,
    SendChatMessageUseCaseDep,
)
from src.modules.messages.transport.http.schemas import (
    ChannelMessagePageResponse,
    ChannelMessageResponse,
    ChatMessagePageResponse,
    ChatMessageResponse,
    MessageCreateRequest,
    MessageEditRequest,
)

channel_message_router = APIRouter(
    prefix="/channels/{channel_id}/messages",
    tags=["Channel Messages"],
)
chat_message_router = APIRouter(
    prefix="/chats/{chat_id}/messages",
    tags=["Chat Messages"],
)


@channel_message_router.post("")
async def send_channel_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    use_case: SendChannelMessageUseCaseDep,
    channel_id: UUID,
) -> ChannelMessageResponse:
    message = await use_case(
        channel_id=channel_id,
        sender_id=user_id,
        data=MessageCreateData(**data.model_dump()),
    )
    return ChannelMessageResponse.model_validate(message)


@chat_message_router.post("")
async def send_chat_message(
    data: MessageCreateRequest,
    user_id: UserIdDep,
    use_case: SendChatMessageUseCaseDep,
    chat_id: UUID,
) -> ChatMessageResponse:
    message = await use_case(
        chat_id=chat_id,
        sender_id=user_id,
        data=MessageCreateData(**data.model_dump()),
    )
    return ChatMessageResponse.model_validate(message)


@channel_message_router.get("")
async def list_channel_messages(
    channel_id: UUID,
    user_id: UserIdDep,
    use_case: ListChannelMessagesUseCaseDep,
    limit: int = Query(20, gt=0, le=100),
    before_cursor: str | None = Query(None, max_length=128),
    after_cursor: str | None = Query(None, max_length=128),
) -> ChannelMessagePageResponse:
    page = await use_case(
        channel_id=channel_id,
        user_id=user_id,
        limit=limit,
        before_cursor=before_cursor,
        after_cursor=after_cursor,
    )
    return ChannelMessagePageResponse.model_validate(page)


@chat_message_router.get("")
async def list_chat_messages(
    chat_id: UUID,
    user_id: UserIdDep,
    use_case: ListChatMessagesUseCaseDep,
    mark_chat_as_read_use_case: MarkChatAsReadUseCaseDep,
    limit: int = Query(20, gt=0, le=100),
    before_cursor: str | None = Query(None, max_length=128),
    after_cursor: str | None = Query(None, max_length=128),
) -> ChatMessagePageResponse:
    page = await use_case(
        chat_id=chat_id,
        user_id=user_id,
        limit=limit,
        before_cursor=before_cursor,
        after_cursor=after_cursor,
    )

    if page.items:
        # listing a chat's messages auto-advances the caller's
        # last-read cursor. Reuses chats' own mark-as-read use case (best
        # effort — a failure here shouldn't fail the read the user asked
        # for) instead of adding new cross-module write plumbing.
        max_seq = max(m.sequence for m in page.items)
        await mark_chat_as_read_use_case(
            chat_id=chat_id, user_id=user_id, up_to_sequence=max_seq
        )

    return ChatMessagePageResponse.model_validate(page)


@channel_message_router.patch("/{message_id}")
async def edit_channel_message(
    channel_id: UUID,
    message_id: UUID,
    data: MessageEditRequest,
    user_id: UserIdDep,
    use_case: EditMessageUseCaseDep,
) -> ChannelMessageResponse:
    message = await use_case(
        message_id=message_id,
        sender_id=user_id,
        data=MessageEditData(**data.model_dump()),
        channel_id=channel_id,
    )
    return ChannelMessageResponse.model_validate(message)


@chat_message_router.patch("/{message_id}")
async def edit_chat_message(
    chat_id: UUID,
    message_id: UUID,
    data: MessageEditRequest,
    user_id: UserIdDep,
    use_case: EditMessageUseCaseDep,
) -> ChatMessageResponse:
    message = await use_case(
        message_id=message_id,
        sender_id=user_id,
        data=MessageEditData(**data.model_dump()),
        chat_id=chat_id,
    )
    return ChatMessageResponse.model_validate(message)


@channel_message_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel_message(
    channel_id: UUID,
    message_id: UUID,
    user_id: UserIdDep,
    use_case: DeleteMessageUseCaseDep,
) -> None:
    await use_case(message_id=message_id, user_id=user_id, channel_id=channel_id)


@chat_message_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(
    chat_id: UUID,
    message_id: UUID,
    user_id: UserIdDep,
    use_case: DeleteMessageUseCaseDep,
) -> None:
    await use_case(message_id=message_id, user_id=user_id, chat_id=chat_id)
