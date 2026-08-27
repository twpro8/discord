from typing import Protocol

from src.modules.email.domain.entities.dtos import OutboundEmail, ProviderReceipt


class EmailProvider(Protocol):
    """Port for the outbound delivery mechanism (SMTP today, SES/SendGrid/
    Mailgun/Resend later — each a new `adapters/providers/*_provider.py`
    implementing this Protocol, selected via `settings.EMAIL_PROVIDER`).
    Never imported outside `adapters/`/`transport/tasks/`."""

    async def send(self, message: OutboundEmail) -> ProviderReceipt: ...
