from uuid import UUID

from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import UserIdDep
from src.modules.chats.domain.entities.dtos import ChatCreateData, ChatUpdateData
from src.modules.chats.transport.http.dependencies import (
    AddMemberUseCaseDep,
    CreateChatUseCaseDep,
    GetChatDetailsUseCaseDep,
    GetChatsUseCaseDep,
    LeaveChatUseCaseDep,
    ListMembersUseCaseDep,
    MarkChatAsReadUseCaseDep,
    RemoveMemberUseCaseDep,
    UpdateChatUseCaseDep,
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
from src.modules.messages.transport.http.router import chat_message_router
from src.shared.schemas.bridge import unsettable_from_request

router = APIRouter(prefix="/chats", tags=["Chats"])
router.include_router(chat_message_router, prefix="/{chat_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    create_chat_use_case: CreateChatUseCaseDep,
    get_chat_details_use_case: GetChatDetailsUseCaseDep,
    data: ChatCreateRequest,
) -> ChatSummaryResponse:
    chat = await create_chat_use_case(
        creator_id=current_user_id,
        data=ChatCreateData(**data.model_dump()),
    )

    details = await get_chat_details_use_case(chat_id=chat.id, user_id=current_user_id)
    return ChatSummaryAdapter.validate_python(details)


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_chats(
    current_user_id: UserIdDep,
    use_case: GetChatsUseCaseDep,
    limit: int = Query(20, gt=0, le=100),
    cursor: str | None = Query(None, max_length=128),
) -> ChatSummaryPageResponse:
    page = await use_case(user_id=current_user_id, limit=limit, cursor=cursor)
    return ChatSummaryPageResponse.model_validate(page)


@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat_details(
    chat_id: UUID,
    current_user_id: UserIdDep,
    use_case: GetChatDetailsUseCaseDep,
) -> ChatSummaryResponse:
    details = await use_case(chat_id=chat_id, user_id=current_user_id)
    return ChatSummaryAdapter.validate_python(details)


@router.patch("/{chat_id}", status_code=status.HTTP_200_OK)
async def update_chat(
    chat_id: UUID,
    current_user_id: UserIdDep,
    update_chat_use_case: UpdateChatUseCaseDep,
    get_chat_details_use_case: GetChatDetailsUseCaseDep,
    data: ChatUpdateRequest,
) -> ChatSummaryResponse:
    await update_chat_use_case(
        chat_id=chat_id,
        user_id=current_user_id,
        update_data=unsettable_from_request(data, ChatUpdateData),
    )

    details = await get_chat_details_use_case(chat_id=chat_id, user_id=current_user_id)
    return ChatSummaryAdapter.validate_python(details)


@router.get("/{chat_id}/members", status_code=status.HTTP_200_OK)
async def list_members(
    chat_id: UUID,
    current_user_id: UserIdDep,
    use_case: ListMembersUseCaseDep,
) -> list[ChatMemberResponse]:
    members = await use_case(chat_id=chat_id, user_id=current_user_id)
    return [ChatMemberResponse.model_validate(m) for m in members]


@router.post("/{chat_id}/members", status_code=status.HTTP_200_OK)
async def add_member(
    chat_id: UUID,
    current_user_id: UserIdDep,
    use_case: AddMemberUseCaseDep,
    data: AddMemberRequest,
) -> AddMemberResponse:
    result = await use_case(
        chat_id=chat_id,
        user_id=current_user_id,
        user_ids=data.user_ids,
    )
    return AddMemberResponse.model_validate(result)


@router.delete(
    "/{chat_id}/members/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_member(
    chat_id: UUID,
    target_user_id: UUID,
    current_user_id: UserIdDep,
    use_case: RemoveMemberUseCaseDep,
) -> None:
    await use_case(
        chat_id=chat_id,
        user_id=current_user_id,
        target_user_id=target_user_id,
    )


@router.post("/{chat_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_chat(
    chat_id: UUID,
    current_user_id: UserIdDep,
    use_case: LeaveChatUseCaseDep,
) -> None:
    await use_case(chat_id=chat_id, user_id=current_user_id)


@router.post("/{chat_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_chat_as_read(
    chat_id: UUID,
    current_user_id: UserIdDep,
    use_case: MarkChatAsReadUseCaseDep,
    data: MarkAsReadRequest | None = None,
) -> None:
    await use_case(
        chat_id=chat_id,
        user_id=current_user_id,
        up_to_sequence=data.up_to_sequence if data else None,
    )
