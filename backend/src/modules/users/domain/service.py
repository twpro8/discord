from uuid import UUID

from src.modules.users.application.unit_of_work import UserUnitOfWork
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.schemas import User
from src.modules.users.transport.http.schemas import UserUpdateRequest
from src.shared.services import BaseService


class UserService(BaseService):
    def __init__(self, user_unit_of_work: UserUnitOfWork):
        self.uow = user_unit_of_work

    async def get_user(self, user_id: UUID) -> User:
        user = await self.uow.users.get_one(id=user_id, is_active=True)
        if not user:
            raise UserNotFoundError
        return user

    async def update(self, user_id: UUID, data: UserUpdateRequest) -> User:
        return await self.uow.users.update(user_id, data, exclude_unset=True)

    async def delete(self, user: User) -> None:
        user.mark_as_inactive()
        await self.uow.users.update(user.id, user)
        await self.uow.commit()
