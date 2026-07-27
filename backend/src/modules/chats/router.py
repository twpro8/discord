from fastapi import APIRouter, Query, status

from src.modules.chats.dependencies import ChatServiceDep
from src.modules.chats.schemas import ChatCreateRequest, ChatSummaryPage
from src.modules.messages.router import chat_message_router
from src.modules.users.transport.http.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["Chats"])
router.include_router(chat_message_router, prefix="/{chat_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    service: ChatServiceDep,
    data: ChatCreateRequest,
) -> ChatCreateRequest:
    await service.create_chat(current_user_id, data)
    return data


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_chats(
    current_user_id: UserIdDep,
    service: ChatServiceDep,
    limit: int = Query(20, gt=0, le=100),
    cursor: str | None = Query(None, max_length=128),
) -> ChatSummaryPage:
    return await service.get_chats(current_user_id, limit, cursor)
