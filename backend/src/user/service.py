from uuid import UUID

from src.core.services import BaseService
from src.user.exceptions import UserNotFoundError
from src.user.schemas import User
from src.user.unit_of_work import UserUnitOfWork


class UserService(BaseService):

    def __init__(self, user_unit_of_work: UserUnitOfWork):
        self.uow = user_unit_of_work

    async def get_user(self, user_id: UUID) -> User:
        user = await self.uow.users.get_one(id=user_id)
        if not user:
            raise UserNotFoundError
        return user
