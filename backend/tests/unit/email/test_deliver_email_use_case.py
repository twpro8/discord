from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid4

import pytest

from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from src.modules.email.domain.exceptions import (
    EmailDeliveryFailed,
    EmailMessageNotFoundError,
    TemplateRenderError,
)
from src.modules.email.usecases.deliver_email import DeliverEmailUseCase
from src.shared.errors import TransientError
from tests.unit.email.fakes import (
    FakeEmailMessageRepository,
    FakeEmailProvider,
    FakeTemplateRenderer,
)
from tests.unit.fakes import FakeTransaction

_TEMPLATE = EmailTemplateName.GENERIC_NOTIFICATION
_CONTEXT = {"recipient_name": "User", "message": "hi"}


async def _pending_message_id(repository: FakeEmailMessageRepository) -> UUID:
    message = await repository.create(
        EmailMessageCreate(
            idempotency_key=None,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )
    return message.id


async def test_delivers_successfully_and_marks_sent() -> None:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    provider = FakeEmailProvider()
    renderer = FakeTemplateRenderer()
    message_id = await _pending_message_id(repository)
    use_case = DeliverEmailUseCase(tx, repository, renderer, provider)

    dto = await use_case(
        message_id=message_id,
        to="user@example.com",
        template=_TEMPLATE,
        context=_CONTEXT,
    )

    assert dto.status == EmailStatus.SENT
    assert dto.provider_message_id == "provider-message-id"
    assert tx.committed
    assert len(provider.sent) == 1
    assert provider.sent[0].to == "user@example.com"


async def test_already_sent_message_is_a_safe_noop() -> None:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    provider = FakeEmailProvider()
    renderer = FakeTemplateRenderer()
    message_id = await _pending_message_id(repository)
    await repository.mark_sent(message_id, provider_message_id="already-sent")
    use_case = DeliverEmailUseCase(tx, repository, renderer, provider)

    dto = await use_case(
        message_id=message_id,
        to="user@example.com",
        template=_TEMPLATE,
        context=_CONTEXT,
    )

    assert dto.status == EmailStatus.SENT
    assert provider.sent == []  # never re-sent
    assert not tx.committed  # no write needed for a redelivered no-op


async def test_message_not_found_raises() -> None:
    tx = FakeTransaction()
    use_case = DeliverEmailUseCase(
        tx, FakeEmailMessageRepository(), FakeTemplateRenderer(), FakeEmailProvider()
    )

    with pytest.raises(EmailMessageNotFoundError):
        await use_case(
            message_id=uuid4(),
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )


class _RaisingTemplateRenderer(FakeTemplateRenderer):
    async def render(
        self, template: EmailTemplateName, context: Mapping[str, Any]
    ) -> Any:
        raise TemplateRenderError("missing variable")


async def test_template_render_error_marks_failed_not_retrying() -> None:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    message_id = await _pending_message_id(repository)
    use_case = DeliverEmailUseCase(
        tx, repository, _RaisingTemplateRenderer(), FakeEmailProvider()
    )

    with pytest.raises(TemplateRenderError):
        await use_case(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )

    assert repository.messages[message_id].status == EmailStatus.FAILED


async def test_transient_provider_error_marks_retrying() -> None:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    message_id = await _pending_message_id(repository)
    provider = FakeEmailProvider(error=TransientError("SMTP connection refused"))
    use_case = DeliverEmailUseCase(tx, repository, FakeTemplateRenderer(), provider)

    with pytest.raises(TransientError):
        await use_case(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )

    assert repository.messages[message_id].status == EmailStatus.RETRYING


async def test_permanent_provider_error_marks_failed() -> None:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    message_id = await _pending_message_id(repository)
    provider = FakeEmailProvider(error=EmailDeliveryFailed("hard bounce"))
    use_case = DeliverEmailUseCase(tx, repository, FakeTemplateRenderer(), provider)

    with pytest.raises(EmailDeliveryFailed):
        await use_case(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )

    assert repository.messages[message_id].status == EmailStatus.FAILED
