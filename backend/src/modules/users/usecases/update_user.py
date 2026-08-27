from uuid import UUID

from src.core.cache import Cache
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.exceptions import UserAlreadyExistsError
from src.modules.users.domain.repositories.user_unit_of_work import UserUnitOfWork
from src.modules.users.domain.value_objects.email import Email
from src.modules.users.domain.value_objects.username import Username
from src.modules.users.usecases.get_user_by_id import cache_key
from src.shared.domain.unset import set_fields


class UpdateUserUseCase:
    def __init__(self, uow: UserUnitOfWork, cache: Cache) -> None:
        self._uow = uow
        self._cache = cache

    async def __call__(self, *, user_id: UUID, data: UserUpdate) -> UserDTO:
        updates = set_fields(data)
        if "username" in updates:
            username = Username(updates["username"])
        if "email" in updates:
            email = Email(updates["email"])

        if "username" in updates:
            existing = await self._uow.users.get_by_username(str(username))
            if existing is not None and existing.id != user_id:
                raise UserAlreadyExistsError
        if "email" in updates:
            existing = await self._uow.users.get_by_email(str(email))
            if existing is not None and existing.id != user_id:
                raise UserAlreadyExistsError

        user = await self._uow.users.update(user_id, data)
        await self._uow.commit()
        await self._cache.delete(cache_key(user_id))
        return user_to_dto(user)
