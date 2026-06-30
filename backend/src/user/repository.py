from typing import Any
from uuid import UUID

from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core.repositories import BaseRepository
from src.user.exceptions import UserAlreadyExistsError
from src.user.models import UserOrm
from src.user.schemas import User
from src.user.mappers import UserMapper


class UserRepository(BaseRepository[UserOrm, User]):
    model = UserOrm
    mapper = UserMapper

    async def create(self, data: BaseModel) -> User:
        try:
            user = await super().create(data)
        except IntegrityError:
            raise UserAlreadyExistsError
        return user

    async def update(
        self,
        id_: UUID,
        data: BaseModel,
        exclude_unset: bool = False,
        **filter_by: Any,
    ) -> User:
        try:
            user = await super().update(id_, data, exclude_unset)
        except IntegrityError as e:
            cause = getattr(e.orig, "__cause__", None)
            constraint = getattr(cause, "constraint_name", None)
            if isinstance(cause, UniqueViolationError):
                match constraint:
                    case "users_email_key":
                        raise UserAlreadyExistsError("Email already exists") from e
                    case "users_username_key":
                        raise UserAlreadyExistsError("Username already exists") from e
            raise
        return user
