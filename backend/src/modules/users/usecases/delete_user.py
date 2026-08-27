from uuid import UUID

from src.core.cache import Cache
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.usecases.get_user_by_id import cache_key
from src.shared.domain.transaction import Transaction


class DeleteUserUseCase:
    def __init__(
        self, tx: Transaction, user_repository: UserRepository, cache: Cache
    ) -> None:
        self._tx = tx
        self._users = user_repository
        self._cache = cache

    async def __call__(self, *, user_id: UUID) -> None:
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UserNotFoundError

        user.mark_as_inactive()
        await self._users.update(user.id, UserUpdate(is_active=False))
        await self._tx.commit()
        await self._cache.delete(cache_key(user_id))
