from uuid import uuid4

from src.modules.email.application.queries.get_email_status import (
    GetEmailStatusQuery,
    GetEmailStatusQueryHandler,
)
from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from tests.unit.email.fakes import FakeEmailMessageRepository


async def test_returns_dto_for_existing_message() -> None:
    repository = FakeEmailMessageRepository()
    message = await repository.create(
        EmailMessageCreate(
            idempotency_key=None,
            to="user@example.com",
            template=EmailTemplateName.GENERIC_NOTIFICATION,
            context={},
        )
    )
    handler = GetEmailStatusQueryHandler(repository)

    result = await handler.handle(GetEmailStatusQuery(message_id=message.id))

    assert result.is_ok
    assert result.value.id == message.id


async def test_returns_err_for_missing_message() -> None:
    handler = GetEmailStatusQueryHandler(FakeEmailMessageRepository())

    result = await handler.handle(GetEmailStatusQuery(message_id=uuid4()))

    assert result.is_err
    assert isinstance(result.error, EmailMessageNotFoundError)
