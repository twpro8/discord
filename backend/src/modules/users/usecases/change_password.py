from uuid import UUID

from src.core.cache import Cache
from src.core.security.hashing import hash_password, verify_password
from src.modules.users.domain.entities.dtos import UserUpdate
from src.modules.users.domain.exceptions import (
    IncorrectPasswordError,
    UserNotFoundError,
)
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.usecases.get_user_by_id import cache_key
from src.shared.domain.transaction import Transaction


class ChangePasswordUseCase:
    def __init__(
        self, tx: Transaction, user_repository: UserRepository, cache: Cache
    ) -> None:
        self._tx = tx
        self._users = user_repository
        self._cache = cache

    async def __call__(
        self, *, user_id: UUID, current_password: str, new_password: str
    ) -> None:
        user = await self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise UserNotFoundError
        if not verify_password(current_password, user.password_hash):
            raise IncorrectPasswordError

        await self._users.update(
            user_id, UserUpdate(password_hash=hash_password(new_password))
        )
        await self._tx.commit()
        await self._cache.delete(cache_key(user_id))
