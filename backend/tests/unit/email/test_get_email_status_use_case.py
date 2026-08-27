from uuid import uuid4

import pytest

from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.exceptions import EmailMessageNotFoundError
from src.modules.email.usecases.get_email_status import GetEmailStatusUseCase
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
    use_case = GetEmailStatusUseCase(repository)

    dto = await use_case(message_id=message.id)

    assert dto.id == message.id


async def test_raises_for_missing_message() -> None:
    use_case = GetEmailStatusUseCase(FakeEmailMessageRepository())

    with pytest.raises(EmailMessageNotFoundError):
        await use_case(message_id=uuid4())
