from fastapi import APIRouter, Query, status

from src.api.v1.dependencies import MediatorDep, UserIdDep
from src.modules.chats.application.commands.create_chat import CreateChatCommand
from src.modules.chats.application.queries.get_chats import GetChatsQuery
from src.modules.chats.domain.entities.dtos import ChatCreateData, ChatSummaryPage
from src.modules.chats.transport.http.schemas import (
    ChatCreateRequest,
    ChatSummaryPageResponse,
)
from src.modules.messages.module import get_chat_message_router
from src.shared.errors import LumiereError
from src.shared.result import Result

router = APIRouter(prefix="/chats", tags=["Chats"])
router.include_router(get_chat_message_router(), prefix="/{chat_id}")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_chat(
    current_user_id: UserIdDep,
    mediator: MediatorDep,
    data: ChatCreateRequest,
) -> ChatCreateRequest:
    result = await mediator.send(
        CreateChatCommand(
            creator_id=current_user_id,
            data=ChatCreateData(**data.model_dump()),
        )
    )
    if result.is_err:
        raise result.error
    return data


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
