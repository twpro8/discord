from uuid import UUID

from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.entities.message import Message
from src.modules.messages.domain.exceptions import (
    MessageDeletePermissionError,
    MessageNotFoundError,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)
from src.modules.servers.public.facade import ServersFacade
from src.shared.errors import LumiereError


class DeleteMessageUseCase:
    def __init__(
        self,
        uow: MessageUnitOfWork,
        chats_facade: ChatsFacade,
        servers_facade: ServersFacade,
    ) -> None:
        self._uow = uow
        self._chats_facade = chats_facade
        self._servers_facade = servers_facade

    async def __call__(
        self,
        *,
        message_id: UUID,
        user_id: UUID,
        chat_id: UUID | None = None,
        channel_id: UUID | None = None,
    ) -> Message:
        message = await self._uow.messages.find_by_id(message_id)
        if message is None:
            raise MessageNotFoundError

        if (chat_id is not None and message.chat_id != chat_id) or (
            channel_id is not None and message.channel_id != channel_id
        ):
            raise MessageNotFoundError

        is_sender = message.sender_id == user_id
        is_owner = False

        if not is_sender:
            if message.chat_id is not None:
                try:
                    await self._chats_facade.assert_is_chat_owner(
                        user_id, message.chat_id
                    )
                    is_owner = True
                except LumiereError:
                    is_owner = False
            else:
                assert message.channel_id is not None
                channel = await self._uow.channels.find_by_id(message.channel_id)
                if channel is not None:
                    try:
                        await self._servers_facade.assert_is_server_owner(
                            user_id, channel.server_id
                        )
                        is_owner = True
                    except LumiereError:
                        is_owner = False

        if not (is_sender or is_owner):
            raise MessageDeletePermissionError

        deleted = await self._uow.messages.soft_delete(message_id)
        await self._uow.commit()
        return deleted
