from src.core.config import Settings
from src.modules.email.adapters.providers.smtp_provider import SmtpEmailProvider
from src.modules.email.domain.gateways.email_provider import EmailProvider


def build_email_provider(settings: Settings) -> EmailProvider:
    """Provider selection seam for SES/SendGrid/Mailgun/Resend later: add a
    branch here plus a new `adapters/providers/*_provider.py` adapter
    implementing `EmailProvider` — no application-layer code changes."""
    if settings.EMAIL_PROVIDER == "smtp":
        return SmtpEmailProvider(
            host=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=settings.SMTP_TLS,
            use_ssl=settings.SMTP_SSL,
        )
    raise ValueError(f"Unsupported EMAIL_PROVIDER: {settings.EMAIL_PROVIDER}")
