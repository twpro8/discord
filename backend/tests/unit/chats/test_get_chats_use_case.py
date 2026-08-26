from uuid import uuid4

from src.modules.chats.domain.entities.dtos import ChatSummaryPage
from src.modules.chats.usecases.get_chats import GetChatsUseCase
from tests.unit.chats.fakes import FakeChatRepository


async def test_returns_repository_page() -> None:
    chats = FakeChatRepository()
    chats.summary_page = ChatSummaryPage(items=[], next_cursor="abc", total=3)
    use_case = GetChatsUseCase(chats)

    result = await use_case(user_id=uuid4(), limit=20, cursor=None)

    assert result is chats.summary_page
