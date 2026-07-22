from uuid import UUID

from src.core.permissions import assert_is_chat_member
from src.message.schemas import (
    ChannelMessage,
    ChatMessage,
    MessageCreate,
    MessageCreateRequest,
)
from src.message.unit_of_work import MessageUnitOfWork


class MessageService:
    def __init__(self, message_unit_of_work: MessageUnitOfWork) -> None:
        self.uow = message_unit_of_work

    async def send_channel_message(
        self,
        channel_id: UUID,
        sender_id: UUID,
        data: MessageCreateRequest,
    ) -> ChannelMessage:
        # TODO: assert is channel member
        sequence = await self.uow.channels.increment_sequence(channel_id)
        message = await self.uow.messages.create(
            MessageCreate(
                channel_id=channel_id,
                sender_id=sender_id,
                sequence=sequence,
                **data.model_dump(),
            )
        )
        await self.uow.commit()
        return ChannelMessage(**message.model_dump(exclude={"chat_id"}))

    async def send_chat_message(
        self,
        chat_id: UUID,
        sender_id: UUID,
        data: MessageCreateRequest,
    ) -> ChatMessage:
        await assert_is_chat_member(self.uow, sender_id, chat_id)
        sequence = await self.uow.chats.increment_sequence(chat_id)
        message = await self.uow.messages.create(
            MessageCreate(
                chat_id=chat_id,
                sender_id=sender_id,
                sequence=sequence,
                **data.model_dump(),
            )
        )
        await self.uow.commit()
        return ChatMessage(**message.model_dump(exclude={"channel_id"}))
