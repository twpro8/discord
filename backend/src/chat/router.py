from fastapi import APIRouter, status

from src.chat.dependencies import ChatServiceDep
from src.chat.schemas import ChatCreateRequestSchema, ChatSchema
from src.user.dependencies import UserIdDep

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    service: ChatServiceDep,
    data: ChatCreateRequestSchema,
) -> ChatCreateRequestSchema:
    await service.create_chat(current_user_id, data)
    return data
