from src.modules.email.application.commands.send_email import (
    SendEmailCommand,
    SendEmailCommandHandler,
)
from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from tests.dependency_overrides.job_dispatcher import FakeJobDispatcher
from tests.unit.email.fakes import FakeEmailMessageRepository, FakeEmailUnitOfWork


def _handler() -> tuple[
    SendEmailCommandHandler,
    FakeEmailUnitOfWork,
    FakeEmailMessageRepository,
    FakeJobDispatcher,
]:
    repository = FakeEmailMessageRepository()
    uow = FakeEmailUnitOfWork(repository)
    dispatcher = FakeJobDispatcher()
    return SendEmailCommandHandler(uow, dispatcher), uow, repository, dispatcher


async def test_creates_pending_message_commits_and_enqueues_delivery() -> None:
    handler, uow, _repository, dispatcher = _handler()

    result = await handler.handle(
        SendEmailCommand(
            to="User@Example.com",
            template=EmailTemplateName.GENERIC_NOTIFICATION,
            context={"recipient_name": "User", "message": "hi"},
        )
    )

    assert result.is_ok
    message = result.value
    assert message.to == "user@example.com"
    assert message.status == EmailStatus.PENDING
    assert uow.committed

    assert len(dispatcher.calls) == 1
    task_name, payload, queue = dispatcher.calls[0]
    assert task_name == "email.send"
    assert payload["message_id"] == str(message.id)
    assert payload["to"] == "user@example.com"
    assert payload["template"] == EmailTemplateName.GENERIC_NOTIFICATION.value
    assert queue == "default"


async def test_invalid_email_address_returns_err_without_enqueuing() -> None:
    handler, uow, _repository, dispatcher = _handler()

    result = await handler.handle(
        SendEmailCommand(
            to="not-an-email",
            template=EmailTemplateName.GENERIC_NOTIFICATION,
            context={},
        )
    )

    assert result.is_err
    assert not uow.committed
    assert dispatcher.calls == []


async def test_idempotency_key_returns_existing_without_duplicate_enqueue() -> None:
    handler, _uow, repository, dispatcher = _handler()
    command = SendEmailCommand(
        to="user@example.com",
        template=EmailTemplateName.GENERIC_NOTIFICATION,
        context={"recipient_name": "User", "message": "hi"},
        idempotency_key="welcome-email:123",
    )

    first = await handler.handle(command)
    second = await handler.handle(command)

    assert first.is_ok and second.is_ok
    assert first.value.id == second.value.id
    assert len(repository.messages) == 1
    assert len(dispatcher.calls) == 1
