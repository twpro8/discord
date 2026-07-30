import json
from dataclasses import asdict, dataclass
from datetime import datetime
from uuid import UUID

from src.core.cache import Cache
from src.modules.users.domain.entities.dtos import UserDTO, user_to_dto
from src.modules.users.domain.exceptions import UserNotFoundError
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.shared.application.query import Query
from src.shared.result import Result

_CACHE_TTL_SECONDS = 60


def cache_key(user_id: UUID) -> str:
    return f"users:{user_id}"


def _dto_from_cache(raw: str) -> UserDTO:
    data = json.loads(raw)
    return UserDTO(
        id=UUID(data["id"]),
        name=data["name"],
        username=data["username"],
        email=data["email"],
        avatar_url=data["avatar_url"],
        is_active=data["is_active"],
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


@dataclass(frozen=True, kw_only=True)
class GetUserByIDQuery(Query):
    user_id: UUID


class GetUserByIDQueryHandler:
    """Cache-aside read: a hit avoids the DB round trip entirely; a miss
    reads through and populates the cache for the next call. Caches the
    UserDTO shape, never the entity (which would put password_hash in
    Redis)."""

    def __init__(self, user_repository: UserRepository, cache: Cache) -> None:
        self._users = user_repository
        self._cache = cache

    async def handle(
        self, query: GetUserByIDQuery
    ) -> Result[UserDTO, UserNotFoundError]:
        key = cache_key(query.user_id)
        if cached := await self._cache.get(key):
            return Result.ok(_dto_from_cache(cached))

        user = await self._users.get_by_id(query.user_id)
        if user is None or not user.is_active:
            return Result.err(UserNotFoundError())

        dto = user_to_dto(user)
        await self._cache.set(
            key, json.dumps(asdict(dto), default=str), ttl_seconds=_CACHE_TTL_SECONDS
        )
        return Result.ok(dto)
