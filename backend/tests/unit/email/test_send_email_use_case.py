from src.modules.email.domain.enums import EmailStatus, EmailTemplateName
from src.modules.email.usecases.send_email import SendEmailUseCase
from tests.dependency_overrides.job_dispatcher import FakeJobDispatcher
from tests.unit.email.fakes import FakeEmailMessageRepository
from tests.unit.fakes import FakeTransaction


def _use_case() -> tuple[
    SendEmailUseCase,
    FakeTransaction,
    FakeEmailMessageRepository,
    FakeJobDispatcher,
]:
    repository = FakeEmailMessageRepository()
    tx = FakeTransaction()
    dispatcher = FakeJobDispatcher()
    return SendEmailUseCase(tx, repository, dispatcher), tx, repository, dispatcher


async def test_creates_pending_message_commits_and_enqueues_delivery() -> None:
    use_case, tx, _repository, dispatcher = _use_case()

    message = await use_case(
        to="User@Example.com",
        template=EmailTemplateName.GENERIC_NOTIFICATION,
        context={"recipient_name": "User", "message": "hi"},
    )

    assert message.to == "user@example.com"
    assert message.status == EmailStatus.PENDING
    assert tx.committed

    assert len(dispatcher.calls) == 1
    task_name, payload, queue = dispatcher.calls[0]
    assert task_name == "email.send"
    assert payload["message_id"] == str(message.id)
    assert payload["to"] == "user@example.com"
    assert payload["template"] == EmailTemplateName.GENERIC_NOTIFICATION.value
    assert queue == "default"


async def test_idempotency_key_returns_existing_without_duplicate_enqueue() -> None:
    use_case, _tx, repository, dispatcher = _use_case()
    to = "user@example.com"
    template = EmailTemplateName.GENERIC_NOTIFICATION
    context = {"recipient_name": "User", "message": "hi"}
    idempotency_key = "welcome-email:123"

    first = await use_case(
        to=to, template=template, context=context, idempotency_key=idempotency_key
    )
    second = await use_case(
        to=to, template=template, context=context, idempotency_key=idempotency_key
    )

    assert first.id == second.id
    assert len(repository.messages) == 1
    assert len(dispatcher.calls) == 1
