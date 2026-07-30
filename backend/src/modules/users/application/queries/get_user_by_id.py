from dataclasses import dataclass
from uuid import UUID

from src.modules.users.domain.entities.user import User
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.shared.application.query import Query
from src.shared.result import Result


@dataclass(frozen=True, kw_only=True)
class GetUserByIDQuery(Query):
    user_id: UUID


class GetUserByIDQueryHandler:
    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    async def handle(self, query: GetUserByIDQuery) -> Result[User, UserNotFoundError]:
        user = await self._users.get_by_id(query.user_id)
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())
        return Result.ok(user)
