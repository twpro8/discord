from uuid import UUID

from src.core.logging import get_logger
from src.core.realtime.manager import RoomMembershipUpdater
from src.core.realtime.rooms import chat_room
from src.modules.chats.public.facade import ChatsFacade
from src.modules.messages.domain.cursor import decode_cursor
from src.modules.messages.domain.entities.dtos import ChatMessagePage
from src.modules.messages.domain.repositories.message_repository import (
    MessageRepository,
)

logger = get_logger(__name__)


class ListChatMessagesUseCase:
    def __init__(
        self,
        message_repository: MessageRepository,
        chats_facade: ChatsFacade,
        room_membership_updater: RoomMembershipUpdater,
    ) -> None:
        self._messages = message_repository
        self._chats_facade = chats_facade
        self._room_membership_updater = room_membership_updater

    async def __call__(
        self,
        *,
        chat_id: UUID,
        user_id: UUID,
        limit: int,
        before_cursor: str | None = None,
        after_cursor: str | None = None,
    ) -> ChatMessagePage:
        await self._chats_facade.assert_is_chat_member(user_id, chat_id)

        await self._join_viewer_to_room(user_id, chat_id)

        before = decode_cursor(before_cursor) if before_cursor else None
        after = decode_cursor(after_cursor) if after_cursor else None

        return await self._messages.list_for_chat(chat_id, limit, before, after)

    async def _join_viewer_to_room(self, user_id: UUID, chat_id: UUID) -> None:
        """Lazily joins this viewer's open connection(s) to the chat's
        room the first time they list its messages, instead of a
        connect-time bulk join across every chat the user has ever been
        in (unbounded at scale — a user in a million chats would create a
        million room-joins on every connect). The room comes into
        existence on its first viewer; ConnectionManager.leave_room
        already tears it down once empty, so no separate close step is
        needed. Best-effort realtime plumbing, not the read the caller
        asked for — must never fail the query.
        """
        try:
            await self._room_membership_updater.join_user_to_room(
                user_id, chat_room(chat_id)
            )
        except Exception:
            logger.exception(
                "realtime.room_join_failed",
                user_id=str(user_id),
                chat_id=str(chat_id),
            )
