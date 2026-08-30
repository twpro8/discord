from dataclasses import replace
from uuid import UUID

from src.core.cache import Cache
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.exceptions import UserAlreadyExistsError
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.usecases.get_user_by_id import cache_key
from src.shared.domain.transaction import Transaction
from src.shared.domain.unset import set_fields


class UpdateUserUseCase:
    def __init__(
        self, tx: Transaction, user_repository: UserRepository, cache: Cache
    ) -> None:
        self._tx = tx
        self._users = user_repository
        self._cache = cache

    async def __call__(self, *, user_id: UUID, data: UserUpdate) -> UserDTO:
        updates = set_fields(data)
        if "username" in updates:
            username = updates["username"].strip()
            data = replace(data, username=username)
            existing = await self._users.get_by_username(username)
            if existing is not None and existing.id != user_id:
                raise UserAlreadyExistsError
        if "email" in updates:
            email = updates["email"].strip().lower()
            data = replace(data, email=email)
            existing = await self._users.get_by_email(email)
            if existing is not None and existing.id != user_id:
                raise UserAlreadyExistsError

        user = await self._users.update(user_id, data)
        await self._tx.commit()
        await self._cache.delete(cache_key(user_id))
        return user_to_dto(user)
