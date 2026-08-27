from uuid import UUID, uuid4

from src.core.cache import Cache
from src.core.config import settings
from src.core.storage import Storage
from src.modules.users.domain.entities.dtos import UserDTO, UserUpdate, user_to_dto
from src.modules.users.domain.exceptions import (
    AvatarTooLargeError,
    StorageNotConfiguredError,
    UnsupportedAvatarFormatError,
)
from src.modules.users.domain.repositories.user_repository import UserRepository
from src.modules.users.usecases.get_user_by_id import cache_key
from src.shared.domain.transaction import Transaction

_ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

_AVATAR_PREFIX = "user_avatar"


class UpdateAvatarUseCase:
    def __init__(
        self,
        tx: Transaction,
        user_repository: UserRepository,
        cache: Cache,
        storage: Storage | None,
    ) -> None:
        self._tx = tx
        self._users = user_repository
        self._cache = cache
        self._storage = storage

    async def __call__(
        self, *, user_id: UUID, content: bytes, content_type: str
    ) -> UserDTO:
        if self._storage is None:
            raise StorageNotConfiguredError
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise UnsupportedAvatarFormatError
        if len(content) > settings.R2_MAX_AVATAR_BYTES:
            raise AvatarTooLargeError

        extension = _ALLOWED_CONTENT_TYPES[content_type]
        key = f"{_AVATAR_PREFIX}/{user_id}{extension}"
        await self._storage.upload_bytes(key, content, content_type=content_type)
        # A short random query param busts browser/edge caches when the key
        # is overwritten in place on re-upload. Unique per upload, so the
        # stored URL changes every time the avatar content changes.
        avatar_url = f"{self._storage.public_url(key)}?v={uuid4().hex[:8]}"

        user = await self._users.update(user_id, UserUpdate(avatar_url=avatar_url))
        await self._tx.commit()
        await self._cache.delete(cache_key(user_id))
        return user_to_dto(user)
