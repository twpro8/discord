from fastapi import APIRouter, Query, status

from src.modules.chats.domain.entities.schemas import ChatCreateRequest, ChatSummaryPage
from src.modules.chats.transport.http.dependencies import (
    CreateChatCommandDep,
    GetChatsQueryDep,
)
from src.modules.messages.transport.http.router import chat_message_router
from src.modules.users.transport.http.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["Chats"])
router.include_router(chat_message_router, prefix="/{chat_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    command: CreateChatCommandDep,
    data: ChatCreateRequest,
) -> ChatCreateRequest:
    await command(current_user_id, data)
    return data


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_chats(
    current_user_id: UserIdDep,
    query: GetChatsQueryDep,
    limit: int = Query(20, gt=0, le=100),
    cursor: str | None = Query(None, max_length=128),
) -> ChatSummaryPage:
    return await query(current_user_id, limit, cursor)
