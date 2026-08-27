from email.message import EmailMessage as MimeMessage
from email.utils import make_msgid

import aiosmtplib

from src.modules.email.domain.entities.dtos import OutboundEmail, ProviderReceipt
from src.modules.email.domain.exceptions import EmailDeliveryFailed
from src.shared.errors import TransientError

# Connection-level failures are worth retrying (a flaky/unreachable SMTP
# relay); a rejection *after* connecting (bad recipient, auth failure,
# server refused the DATA) is a permanent failure — see
# `core.jobs.runner.handle_task_error` for why that distinction matters.
_TRANSIENT_EXCEPTIONS = (
    aiosmtplib.SMTPConnectError,
    aiosmtplib.SMTPConnectTimeoutError,
    aiosmtplib.SMTPTimeoutError,
    aiosmtplib.SMTPReadTimeoutError,
    aiosmtplib.SMTPServerDisconnected,
    ConnectionError,
    OSError,
)


class SmtpEmailProvider:
    """The `EmailProvider` port's default adapter. Swappable for
    SES/SendGrid/Mailgun/Resend later via a new adapter implementing the
    same Protocol — see `infrastructure/providers/factory.py`."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        use_tls: bool,
        use_ssl: bool,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username or None
        self._password = password or None
        self._use_tls = use_tls
        self._use_ssl = use_ssl

    async def send(self, message: OutboundEmail) -> ProviderReceipt:
        mime = MimeMessage()
        mime["Subject"] = message.subject
        mime["From"] = f"{message.from_name} <{message.from_email}>"
        mime["To"] = message.to
        message_id = make_msgid()
        mime["Message-ID"] = message_id

        if message.text_body:
            mime.set_content(message.text_body)
            mime.add_alternative(message.html_body, subtype="html")
        else:
            mime.set_content(message.html_body, subtype="html")

        try:
            await aiosmtplib.send(
                mime,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                start_tls=self._use_tls,
                use_tls=self._use_ssl,
            )
        except _TRANSIENT_EXCEPTIONS as exc:
            raise TransientError(f"SMTP connection failed: {exc}") from exc
        except aiosmtplib.SMTPException as exc:
            raise EmailDeliveryFailed(f"SMTP rejected the message: {exc}") from exc

        return ProviderReceipt(provider_message_id=message_id)
