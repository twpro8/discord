from src.core.security.hashing import verify_password
from src.modules.auth.application.token_helper import issue_tokens
from src.modules.auth.domain.exceptions import IncorrectPasswordError
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.auth.domain.schemas import TokenPair
from src.modules.users.domain.exceptions import UserNotFoundError


class LoginCommand:
    def __init__(self, uow: AbstractAuthUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, username: str, password: str) -> TokenPair:
        user = await self._uow.users.get_by_username(username)
        if not user or not user.is_active:
            raise UserNotFoundError
        if not verify_password(password, user.password_hash):
            raise IncorrectPasswordError
        tokens = await issue_tokens(self._uow, user.id)
        await self._uow.commit()
        return tokens
