from src.modules.email.domain.entities.email_message import EmailMessage
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.domain.value_objects.email_address import EmailAddress
from src.modules.email.infrastructure.persistence.models import EmailMessageOrm


class EmailMessageDataMapper:
    @staticmethod
    def to_entity(model: EmailMessageOrm) -> EmailMessage:
        return EmailMessage(
            id=model.id,
            idempotency_key=model.idempotency_key,
            to=EmailAddress(model.to),
            template=EmailTemplateName(model.template),
            context=dict(model.context),
            status=model.status,
            attempts=model.attempts,
            error_message=model.error_message,
            provider_message_id=model.provider_message_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            sent_at=model.sent_at,
        )
