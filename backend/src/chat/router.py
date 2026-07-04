from fastapi import APIRouter, status, Query

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatCreateRequest, ChatSummaryPage
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["Chats"])


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
