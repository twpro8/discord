from uuid import UUID

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_repository import UserRepository


class GetUserByIDQuery:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def __call__(self, user_id: UUID) -> User:
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UserNotFoundError
        return user
