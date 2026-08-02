from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.chats.application.commands.add_member import AddMemberCommand
from src.modules.chats.application.commands.create_chat import CreateChatCommand
from src.modules.chats.application.commands.leave_chat import LeaveChatCommand
from src.modules.chats.application.commands.mark_chat_as_read import (
    MarkChatAsReadCommand,
)
from src.modules.chats.application.commands.remove_member import RemoveMemberCommand
from src.modules.chats.application.commands.update_chat import UpdateChatCommand
from src.modules.chats.application.queries.get_chat_details import (
    GetChatDetailsQuery,
)
from src.modules.chats.application.queries.get_chats import GetChatsQuery
from src.modules.chats.application.queries.list_members import ListMembersQuery
from src.modules.chats.domain.entities.dtos import (
    ChatCreateData,
    ChatSummary,
    ChatSummaryPage,
    ChatUpdateData,
)
from src.modules.chats.transport.http.schemas import (
    AddMemberRequest,
    AddMemberResponse,
    ChatCreateRequest,
    ChatMemberResponse,
    ChatSummaryAdapter,
    ChatSummaryPageResponse,
    ChatSummaryResponse,
    ChatUpdateRequest,
    MarkAsReadRequest,
)
from src.modules.messages.module import get_chat_message_router
from src.shared.errors import LumiereError
from src.shared.result import Result
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/chats", tags=["Chats"])
router.include_router(get_chat_message_router(), prefix="/{chat_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    data: ChatCreateRequest,
) -> ChatSummaryResponse:
    result = await mediator.send(
        CreateChatCommand(
            creator_id=current_user_id,
            data=ChatCreateData(**data.model_dump()),
        )
    )
    if result.is_err:
        raise result.error

    details: Result[ChatSummary, LumiereError] = await mediator.query(
        GetChatDetailsQuery(chat_id=result.value.id, user_id=current_user_id)
    )
    if details.is_err:
        raise details.error
    return ChatSummaryAdapter.validate_python(details.value)


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_chats(
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    limit: int = Query(20, gt=0, le=100),
    cursor: str | None = Query(None, max_length=128),
) -> ChatSummaryPageResponse:
    result: Result[ChatSummaryPage, LumiereError] = await mediator.query(
        GetChatsQuery(user_id=current_user_id, limit=limit, cursor=cursor)
    )
    if result.is_err:
        raise result.error
    return ChatSummaryPageResponse.model_validate(result.value)


@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat_details(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> ChatSummaryResponse:
    result: Result[ChatSummary, LumiereError] = await mediator.query(
        GetChatDetailsQuery(chat_id=chat_id, user_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return ChatSummaryAdapter.validate_python(result.value)


@router.patch("/{chat_id}", status_code=status.HTTP_200_OK)
async def update_chat(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    data: ChatUpdateRequest,
) -> ChatSummaryResponse:
    result = await mediator.send(
        UpdateChatCommand(
            chat_id=chat_id,
            user_id=current_user_id,
            update_data=unsettable_from_request(data, ChatUpdateData),
        )
    )
    if result.is_err:
        raise result.error

    details: Result[ChatSummary, LumiereError] = await mediator.query(
        GetChatDetailsQuery(chat_id=chat_id, user_id=current_user_id)
    )
    if details.is_err:
        raise details.error
    return ChatSummaryAdapter.validate_python(details.value)


@router.get("/{chat_id}/members", status_code=status.HTTP_200_OK)
async def list_members(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> list[ChatMemberResponse]:
    result = await mediator.query(
        ListMembersQuery(chat_id=chat_id, user_id=current_user_id)
    )
    if result.is_err:
        raise result.error
    return [ChatMemberResponse.model_validate(m) for m in result.value]


@router.post("/{chat_id}/members", status_code=status.HTTP_200_OK)
async def add_member(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    data: AddMemberRequest,
) -> AddMemberResponse:
    result = await mediator.send(
        AddMemberCommand(
            chat_id=chat_id,
            user_id=current_user_id,
            user_ids=data.user_ids,
        )
    )
    if result.is_err:
        raise result.error
    return AddMemberResponse.model_validate(result.value)


@router.delete(
    "/{chat_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    chat_id: UUID,
    target_user_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        RemoveMemberCommand(
            chat_id=chat_id,
            user_id=current_user_id,
            target_user_id=target_user_id,
        )
    )
    if result.is_err:
        raise result.error


@router.post("/{chat_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_chat(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
) -> None:
    result = await mediator.send(
        LeaveChatCommand(chat_id=chat_id, user_id=current_user_id)
    )
    if result.is_err:
        raise result.error


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_chat_as_read(
    chat_id: UUID,
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    data: MarkAsReadRequest | None = None,
) -> None:
    result = await mediator.send(
        MarkChatAsReadCommand(
            chat_id=chat_id,
            user_id=current_user_id,
            up_to_sequence=data.up_to_sequence if data else None,
        )
    )
    if result.is_err:
        raise result.error
