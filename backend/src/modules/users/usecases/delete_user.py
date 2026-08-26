from uuid import UUID

from src.core.cache import Cache
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.modules.users.usecases.get_user_by_id import cache_key


class DeleteUserUseCase:
    def __init__(self, uow: UserUnitOfWork, cache: Cache) -> None:
        self._uow = uow
        self._cache = cache

    async def __call__(self, *, user_id: UUID) -> None:
        user = await self._uow.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UserNotFoundError

        user.mark_as_inactive()
        await self._uow.users.update(user.id, UserUpdate(is_active=False))
        await self._uow.commit()
        await self._cache.delete(cache_key(user_id))
