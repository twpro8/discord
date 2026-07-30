from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.modules.messages.domain.entities.schemas import Message, MessageCreate
from src.modules.messages.domain.repositories.message_unit_of_work import (
    MessageUnitOfWork,
)

# MessageUnitOfWork still composes chats'/channels' repositories directly
# for the same-transaction increment_sequence write; reuse their
# already-built fakes rather than duplicating them here. Permission checks
# go through ChatsFacade/ServersFacade instead (see tests.unit.chats.fakes
# / tests.unit.servers.fakes).
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import FakeChatRepository


class FakeMessageRepository:
    def __init__(self) -> None:
        self.messages: dict[UUID, Message] = {}

    async def create(self, data: MessageCreate) -> Message:
        now = datetime.now(UTC)
        message = Message(
            id=uuid4(),
            sender_id=data.sender_id,
            body=data.body,
            sequence=data.sequence,
            parent_id=data.parent_id,
            is_edited=False,
            is_deleted=False,
            deleted_at=None,
            created_at=now,
            updated_at=now,
            chat_id=data.chat_id,
            channel_id=data.channel_id,
        )
        self.messages[message.id] = message
        return message


class FakeMessageUnitOfWork(MessageUnitOfWork):
    def __init__(
        self,
        messages: FakeMessageRepository,
        chats: FakeChatRepository,
        channels: FakeChannelRepository,
    ) -> None:
        self.messages = messages
        self.chats = chats
        self.channels = channels
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
