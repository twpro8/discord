from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from src.modules.messages.domain.entities.dtos import MessageCreate, MessageEditData
from src.modules.messages.domain.exceptions import (
    MessageEditWindowExpiredError,
    MessageNotFoundError,
    NotMessageSenderError,
)
from src.modules.messages.usecases.edit_message import EditMessageUseCase
from tests.unit.messages.fakes import FakeMessageRepository


async def test_sender_can_edit_within_window() -> None:
    messages = FakeMessageRepository()
    use_case = EditMessageUseCase(messages)
    sender_id, chat_id = uuid4(), uuid4()
    message = await messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )

    updated = await use_case(
        message_id=message.id,
        sender_id=sender_id,
        data=MessageEditData(body="edited"),
    )

    assert updated.body == "edited"
    assert updated.is_edited is True


async def test_rejects_missing_message() -> None:
    use_case = EditMessageUseCase(FakeMessageRepository())

    with pytest.raises(MessageNotFoundError):
        await use_case(
            message_id=uuid4(), sender_id=uuid4(), data=MessageEditData(body="edited")
        )


async def test_rejects_non_sender() -> None:
    messages = FakeMessageRepository()
    use_case = EditMessageUseCase(messages)
    sender_id, chat_id = uuid4(), uuid4()
    message = await messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )

    with pytest.raises(NotMessageSenderError):
        await use_case(
            message_id=message.id,
            sender_id=uuid4(),
            data=MessageEditData(body="edited"),
        )


async def test_rejects_expired_edit_window() -> None:
    messages = FakeMessageRepository()
    use_case = EditMessageUseCase(messages)
    sender_id, chat_id = uuid4(), uuid4()
    message = await messages.create(
        MessageCreate(
            sender_id=sender_id,
            body="hello",
            sequence=1,
            parent_id=None,
            chat_id=chat_id,
        )
    )
    message.created_at = datetime.now(UTC) - timedelta(hours=25)

    with pytest.raises(MessageEditWindowExpiredError):
        await use_case(
            message_id=message.id,
            sender_id=sender_id,
            data=MessageEditData(body="edited"),
        )
