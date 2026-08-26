from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork


class MarkChatAsReadUseCase:
    def __init__(self, uow: ChatUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, up_to_sequence: int | None = None
    ) -> None:
        chat = await services.assert_is_chat_member(
            self._uow.chats, self._uow.members, user_id, chat_id
        )

        target = up_to_sequence if up_to_sequence is not None else chat.last_sequence
        await self._uow.members.update_last_read_seq(chat_id, user_id, target)
        await self._uow.commit()
