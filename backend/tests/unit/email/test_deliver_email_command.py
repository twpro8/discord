from collections.abc import Mapping
from typing import Any
from uuid import UUID, uuid4

from src.modules.email.application.commands.deliver_email import (
    DeliverEmailCommand,
    DeliverEmailCommandHandler,
)
from src.modules.email.domain.entities.dtos import EmailMessageCreate
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from src.modules.email.domain.exceptions import (
    EmailDeliveryFailed,
    EmailMessageNotFoundError,
    TemplateRenderError,
)
from src.shared.errors import TransientError
from tests.unit.email.fakes import (
    FakeEmailMessageRepository,
    FakeEmailProvider,
    FakeEmailUnitOfWork,
    FakeTemplateRenderer,
)

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
    uow = FakeEmailUnitOfWork(repository)
    provider = FakeEmailProvider()
    renderer = FakeTemplateRenderer()
    message_id = await _pending_message_id(repository)
    handler = DeliverEmailCommandHandler(uow, renderer, provider)

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_ok
    assert result.value.status == EmailStatus.SENT
    assert result.value.provider_message_id == "provider-message-id"
    assert uow.committed
    assert len(provider.sent) == 1
    assert provider.sent[0].to == "user@example.com"


async def test_already_sent_message_is_a_safe_noop() -> None:
    repository = FakeEmailMessageRepository()
    uow = FakeEmailUnitOfWork(repository)
    provider = FakeEmailProvider()
    renderer = FakeTemplateRenderer()
    message_id = await _pending_message_id(repository)
    await repository.mark_sent(message_id, provider_message_id="already-sent")
    handler = DeliverEmailCommandHandler(uow, renderer, provider)

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_ok
    assert result.value.status == EmailStatus.SENT
    assert provider.sent == []  # never re-sent
    assert not uow.committed  # no write needed for a redelivered no-op


async def test_message_not_found_returns_err() -> None:
    uow = FakeEmailUnitOfWork(FakeEmailMessageRepository())
    handler = DeliverEmailCommandHandler(
        uow, FakeTemplateRenderer(), FakeEmailProvider()
    )

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=uuid4(),
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_err
    assert isinstance(result.error, EmailMessageNotFoundError)


class _RaisingTemplateRenderer(FakeTemplateRenderer):
    async def render(
        self, template: EmailTemplateName, context: Mapping[str, Any]
    ) -> Any:
        raise TemplateRenderError("missing variable")


async def test_template_render_error_marks_failed_not_retrying() -> None:
    repository = FakeEmailMessageRepository()
    uow = FakeEmailUnitOfWork(repository)
    message_id = await _pending_message_id(repository)
    handler = DeliverEmailCommandHandler(
        uow, _RaisingTemplateRenderer(), FakeEmailProvider()
    )

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_err
    assert isinstance(result.error, TemplateRenderError)
    assert repository.messages[message_id].status == EmailStatus.FAILED


async def test_transient_provider_error_marks_retrying() -> None:
    repository = FakeEmailMessageRepository()
    uow = FakeEmailUnitOfWork(repository)
    message_id = await _pending_message_id(repository)
    provider = FakeEmailProvider(error=TransientError("SMTP connection refused"))
    handler = DeliverEmailCommandHandler(uow, FakeTemplateRenderer(), provider)

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_err
    assert isinstance(result.error, TransientError)
    assert repository.messages[message_id].status == EmailStatus.RETRYING


async def test_permanent_provider_error_marks_failed() -> None:
    repository = FakeEmailMessageRepository()
    uow = FakeEmailUnitOfWork(repository)
    message_id = await _pending_message_id(repository)
    provider = FakeEmailProvider(error=EmailDeliveryFailed("hard bounce"))
    handler = DeliverEmailCommandHandler(uow, FakeTemplateRenderer(), provider)

    result = await handler.handle(
        DeliverEmailCommand(
            message_id=message_id,
            to="user@example.com",
            template=_TEMPLATE,
            context=_CONTEXT,
        )
    )

    assert result.is_err
    assert isinstance(result.error, EmailDeliveryFailed)
    assert repository.messages[message_id].status == EmailStatus.FAILED
