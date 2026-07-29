from src.core.security.hashing import hash_password
from src.modules.auth.domain.entities.schemas import RegisterForm
from src.modules.auth.domain.repositories.auth_unit_of_work import (
    AbstractAuthUnitOfWork,
)
from src.modules.users.domain.entities.schemas import UserCreate
from src.modules.users.domain.entities.user import User
from src.shared.errors import LumiereError
from src.shared.result import Result


class RegisterCommand:
    def __init__(self, uow: AbstractAuthUnitOfWork) -> None:
        self._uow = uow

    async def __call__(self, form_data: RegisterForm) -> Result[User, LumiereError]:
        user_data = UserCreate(
            **form_data.model_dump(),
            password_hash=hash_password(form_data.password),
        )
        user = await self._uow.users.create(user_data)
        await self._uow.commit()
        return Result.ok(user)
