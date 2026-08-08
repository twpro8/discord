from dataclasses import dataclass
from uuid import UUID, uuid4

from src.core.cache import Cache
from src.core.config import settings
from src.core.storage import Storage
from src.modules.users.application.queries.get_user_by_id import cache_key
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.exceptions import (
    AvatarTooLargeError,
    StorageNotConfiguredError,
    UnsupportedAvatarFormatError,
)
from src.modules.users.domain.repositories.user_unit_of_work import (
    UserUnitOfWork,
)
from src.shared.application.command import Command
from src.shared.errors import LumiereError
from src.shared.result import Result

_ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

_AVATAR_PREFIX = "user_avatar"


@dataclass(frozen=True, kw_only=True)
class UpdateAvatarCommand(Command):
    user_id: UUID
    content: bytes
    content_type: str


class UpdateAvatarCommandHandler:
    def __init__(
        self, uow: UserUnitOfWork, cache: Cache, storage: Storage | None
    ) -> None:
        self._uow = uow
        self._cache = cache
        self._storage = storage

    async def handle(
        self, command: UpdateAvatarCommand
    ) -> Result[UserDTO, LumiereError]:
        if self._storage is None:
            return Result.err(StorageNotConfiguredError())
        if command.content_type not in _ALLOWED_CONTENT_TYPES:
            return Result.err(UnsupportedAvatarFormatError())
        if len(command.content) > settings.R2_MAX_AVATAR_BYTES:
            return Result.err(AvatarTooLargeError())

        extension = _ALLOWED_CONTENT_TYPES[command.content_type]
        key = f"{_AVATAR_PREFIX}/{command.user_id}{extension}"
        await self._storage.upload_bytes(
            key, command.content, content_type=command.content_type
        )
        # A short random query param busts browser/edge caches when the key
        # is overwritten in place on re-upload. Unique per upload, so the
        # stored URL changes every time the avatar content changes.
        avatar_url = f"{self._storage.public_url(key)}?v={uuid4().hex[:8]}"

        user = await self._uow.users.update(
            command.user_id, UserUpdate(avatar_url=avatar_url)
        )
        await self._uow.commit()
        await self._cache.delete(cache_key(command.user_id))
        return Result.ok(user_to_dto(user))
