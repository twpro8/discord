from datetime import UTC, datetime

from src.core.logging import get_logger
from src.modules.auth.domain.entities.dtos import TokenPair
from src.modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.modules.auth.usecases.token_helper import issue_tokens
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.public.facade import EmailFacade
from src.modules.users.public.facade import UsersFacade
from src.shared.domain.transaction import Transaction
from src.shared.errors import LumiereError

logger = get_logger(__name__)


class LoginUseCase:
    def __init__(
        self,
        tx: Transaction,
        refresh_token_repository: RefreshTokenRepository,
        users_facade: UsersFacade,
        email_facade: EmailFacade,
    ) -> None:
        self._tx = tx
        self._refresh_tokens = refresh_token_repository
        self._users_facade = users_facade
        self._email_facade = email_facade

    async def __call__(self, *, username: str, password: str) -> TokenPair:
        user = await self._users_facade.verify_credentials(
            username=username,
            plain_password=password,
        )

        tokens = await issue_tokens(self._refresh_tokens, user.id)
        await self._tx.commit()

        # Best-effort notification: a failed/slow email must never block a
        # successful login. See EmailFacade.send_email — this only
        # records the message and enqueues async delivery, it doesn't
        # wait for SMTP. idempotency_key caps this at one notification
        # per user per day, so a burst of rapid re-logins (token refresh
        # flows, multiple tabs) doesn't spam the inbox.
        today = datetime.now(UTC).date().isoformat()
        try:
            await self._email_facade.send_email(
                to=user.email,
                template=EmailTemplateName.GENERIC_NOTIFICATION,
                context={
                    "recipient_name": user.name,
                    "message": "You just logged in to your Lumiere account.",
                },
                idempotency_key=f"login-notification:{user.id}:{today}",
            )
        except LumiereError as error:
            logger.warning(
                "auth.login_notification_failed",
                user_id=str(user.id),
                error=str(error),
            )

        return tokens
