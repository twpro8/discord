from dataclasses import asdict
from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.envelope import EventType
from src.core.realtime.notifier import RealtimeNotifier
from src.core.realtime.rooms import chat_room
from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.entities.dtos import (
    ChatMessage,
    MessageCreate,
    MessageCreateData,
    chat_message_from_message,
)
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)

logger = get_logger(__name__)


class SendChatMessageUseCase:
    def __init__(
        self,
        uow: MessageUnitOfWork,
        chats_facade: ChatsFacade,
        realtime_notifier: RealtimeNotifier,
    ) -> None:
        self._uow = uow
        self._chats_facade = chats_facade
        self._realtime = realtime_notifier

    async def __call__(
        self, *, chat_id: UUID, sender_id: UUID, data: MessageCreateData
    ) -> ChatMessage:
        await self._chats_facade.assert_is_chat_member(sender_id, chat_id)
        sequence = await self._uow.chats.increment_sequence(chat_id)
        message = await self._uow.messages.create(
            MessageCreate(
                chat_id=chat_id,
                sender_id=sender_id,
                sequence=sequence,
                body=data.body,
                parent_id=data.parent_id,
            )
        )

        await self._uow.commit()
        chat_message = chat_message_from_message(message)
        await self._notify(chat_id, chat_message)
        return chat_message

    async def _notify(self, chat_id: UUID, message: ChatMessage) -> None:
        """Fan the new message out to everyone in the chat's room.

        A single publish, not one per member: every member's connection
        is joined to the chat's room either dynamically (at chat
        creation/membership-add time, see chats' Create/AddMember use
        cases) or at connect time for pre-existing memberships (see
        api/v1/ws.py).

        Best effort: a realtime delivery failure must not fail the send the
        caller asked for (matches the codebase's mark-as-read precedent).
        """
        try:
            await self._realtime.publish_to_room(
                room=chat_room(chat_id),
                event_type=EventType.MESSAGE_CREATED,
                payload=asdict(message),
            )
        except Exception:
            logger.exception("realtime.publish_failed", chat_id=str(chat_id))
