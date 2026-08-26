from dataclasses import dataclass
from datetime import UTC, datetime

from src.core.logging import get_logger
from src.modules.auth.application.token_helper import issue_tokens
from src.modules.auth.domain.entities.dtos import TokenPair
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AuthUnitOfWork,
)
from src.modules.email.domain.enums import EmailTemplateName
from src.modules.email.public.facade import EmailFacade
from src.modules.users.public.facade import UsersFacade
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result

logger = get_logger(__name__)


@dataclass(frozen=True, kw_only=True)
class LoginCommand(Command):
    username: str
    password: str


class LoginCommandHandler:
    def __init__(
        self,
        uow: AuthUnitOfWork,
        users_facade: UsersFacade,
        email_facade: EmailFacade,
    ) -> None:
        self._uow = uow
        self._users_facade = users_facade
        self._email_facade = email_facade

    async def handle(self, command: LoginCommand) -> Result[TokenPair, LumiereError]:
        try:
            user = await self._users_facade.verify_credentials(
                username=command.username,
                plain_password=command.password,
            )
        except LumiereError as error:
            return Result.err(error)

        tokens = await issue_tokens(self._uow, user.id)
        await self._uow.commit()

        # Best-effort notification: a failed/slow email must never block a
        # successful login, so its Result is logged, not propagated. See
        # EmailFacade.send_email — this only records the message and
        # enqueues async delivery, it doesn't wait for SMTP. idempotency_key
        # caps this at one notification per user per day, so a burst of
        # rapid re-logins (token refresh flows, multiple tabs) doesn't spam
        # the inbox.
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

        return Result.ok(tokens)
