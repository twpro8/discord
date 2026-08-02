from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.modules.messages.application.commands.edit_message import (
    EditMessageCommand,
    EditMessageCommandHandler,
)
from src.modules.messages.domain.entities.dtos import MessageCreate, MessageEditData
from src.modules.messages.domain.exceptions import (
    MessageEditWindowExpiredError,
    MessageNotFoundError,
    NotMessageSenderError,
)
from tests.unit.channels.fakes import FakeChannelRepository
from tests.unit.chats.fakes import FakeChatRepository
from tests.unit.messages.fakes import FakeMessageRepository, FakeMessageUnitOfWork


def _uow() -> FakeMessageUnitOfWork:
    return FakeMessageUnitOfWork(
        FakeMessageRepository(), FakeChatRepository(), FakeChannelRepository()
    )


async def test_sender_can_edit_within_window() -> None:
    uow = _uow()
    handler = EditMessageCommandHandler(uow)
    sender_id, chat_id = uuid4(), uuid4()
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )

    result = await handler.handle(
        EditMessageCommand(
            message_id=message.id,
            sender_id=sender_id,
            data=MessageEditData(body="edited"),
        )
    )

    assert result.is_ok
    assert result.value.body == "edited"
    assert result.value.is_edited is True
    assert uow.committed


async def test_rejects_missing_message() -> None:
    uow = _uow()
    handler = EditMessageCommandHandler(uow)

    result = await handler.handle(
        EditMessageCommand(
            message_id=uuid4(), sender_id=uuid4(), data=MessageEditData(body="edited")
        )
    )

    assert result.is_err
    assert isinstance(result.error, MessageNotFoundError)


async def test_rejects_non_sender() -> None:
    uow = _uow()
    handler = EditMessageCommandHandler(uow)
    sender_id, chat_id = uuid4(), uuid4()
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )

    result = await handler.handle(
        EditMessageCommand(
            message_id=message.id,
            sender_id=uuid4(),
            data=MessageEditData(body="edited"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, NotMessageSenderError)


async def test_rejects_expired_edit_window() -> None:
    uow = _uow()
    handler = EditMessageCommandHandler(uow)
    sender_id, chat_id = uuid4(), uuid4()
    message = await uow.messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )
    message.created_at = datetime.now(UTC) - timedelta(hours=25)

    result = await handler.handle(
        EditMessageCommand(
            message_id=message.id,
            sender_id=sender_id,
            data=MessageEditData(body="edited"),
        )
    )

    assert result.is_err
    assert isinstance(result.error, MessageEditWindowExpiredError)
