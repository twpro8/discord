from uuid import uuid4

from src.modules.chats.application.queries.get_chats import (
    GetChatsQuery,
    GetChatsQueryHandler,
)
from src.modules.chats.domain.entities.schemas import ChatSummaryPage
from tests.unit.chats.fakes import FakeChatRepository


async def test_returns_repository_page_wrapped_in_ok() -> None:
    chats = FakeChatRepository()
    chats.summary_page = ChatSummaryPage(items=[], next_cursor="abc", total=3)
    handler = GetChatsQueryHandler(chats)

    result = await handler.handle(GetChatsQuery(user_id=uuid4(), limit=20, cursor=None))

    assert result.is_ok
    assert result.value is chats.summary_page
