from src.shared.errors import LumiereError, NotFoundError, ValidationError


class EmailError(LumiereError): ...


class EmailMessageNotFoundError(EmailError, NotFoundError):
    detail = "Email message not found"


class TemplateNotFoundError(EmailError, ValidationError):
    def __init__(self, template: str) -> None:
        super().__init__(f"Unknown email template '{template}'")


class TemplateRenderError(EmailError, ValidationError):
    detail = "Failed to render email template"


class EmailDeliveryFailed(EmailError):
    """A permanent (non-retryable) delivery failure, e.g. a hard SMTP
    rejection. Transient send failures use the shared `TransientError`
    instead so `core.jobs.runner.handle_task_error` retries them."""

    detail = "Failed to deliver email"
