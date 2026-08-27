from src.modules.auth.domain.entities.dtos import RegisterData
from src.modules.users.domain.entities.dtos import UserDTO
from src.modules.users.public.facade import UsersFacade


class RegisterUseCase:
    def __init__(self, users_facade: UsersFacade) -> None:
        self._users_facade = users_facade

    async def __call__(self, *, data: RegisterData) -> UserDTO:
        return await self._users_facade.create_user(
            name=data.name,
            username=data.username,
            email=data.email,
            plain_password=data.password,
        )
