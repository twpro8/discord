from uuid import UUID

from src.modules.chats.domain import services
from src.modules.chats.domain.entities.chat import Chat
from src.modules.chats.domain.entities.dtos import ChatUpdate, ChatUpdateData
from src.modules.chats.domain.repositories.chat_unit_of_work import ChatUnitOfWork


class UpdateChatUseCase:
    def __init__(self, uow: ChatUnitOfWork) -> None:
        self._uow = uow

    async def __call__(
        self, *, chat_id: UUID, user_id: UUID, update_data: ChatUpdateData
    ) -> Chat:
        await services.assert_is_group_chat_owner(
            self._uow.chats, self._uow.members, user_id, chat_id
        )
        updated_chat = await self._uow.chats.update(
            chat_id,
            ChatUpdate(
                name=update_data.name,
                description=update_data.description,
                image_url=update_data.image_url,
            ),
        )

        await self._uow.commit()
        return updated_chat
