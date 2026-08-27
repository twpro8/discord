import pytest

from src.modules.users.domain.exceptions import (
    StorageNotConfiguredError,
    UnsupportedAvatarFormatError,
)
from src.modules.users.usecases.get_user_by_id import cache_key
from src.modules.users.usecases.update_avatar import UpdateAvatarUseCase
from tests.unit.users.fakes import (
    FakeCache,
    FakeStorage,
    FakeUserRepository,
    FakeUserUnitOfWork,
    make_user,
)


async def test_uploads_avatar_and_updates_url() -> None:
    user = make_user()
    storage = FakeStorage(public_base_url="https://files.example.com")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    cache = FakeCache()
    await cache.set(cache_key(user.id), "stale")
    use_case = UpdateAvatarUseCase(uow, cache, storage)

    dto = await use_case(
        user_id=user.id, content=b"fake-png-bytes", content_type="image/png"
    )

    key = f"user_avatar/{user.id}.png"
    assert key in storage.objects
    assert storage.objects[key] == b"fake-png-bytes"
    assert dto.avatar_url is not None
    assert dto.avatar_url.startswith(f"https://files.example.com/{key}?v=")
    assert uow.committed
    assert cache_key(user.id) not in cache.store


async def test_each_upload_gets_a_new_avatar_url() -> None:
    user = make_user()
    storage = FakeStorage(public_base_url="https://files.example.com")
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateAvatarUseCase(uow, FakeCache(), storage)

    first = await use_case(
        user_id=user.id, content=b"fake-png-bytes", content_type="image/png"
    )
    second = await use_case(
        user_id=user.id, content=b"fake-png-bytes", content_type="image/png"
    )

    assert first.avatar_url is not None
    assert first.avatar_url != second.avatar_url
    assert first.avatar_url.startswith(
        f"https://files.example.com/user_avatar/{user.id}.png?v="
    )


async def test_rejects_when_storage_not_configured() -> None:
    user = make_user()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateAvatarUseCase(uow, FakeCache(), None)

    with pytest.raises(StorageNotConfiguredError):
        await use_case(user_id=user.id, content=b"bytes", content_type="image/png")

    assert not uow.committed


async def test_rejects_unsupported_content_type() -> None:
    user = make_user()
    storage = FakeStorage()
    uow = FakeUserUnitOfWork(FakeUserRepository([user]))
    use_case = UpdateAvatarUseCase(uow, FakeCache(), storage)

    with pytest.raises(UnsupportedAvatarFormatError):
        await use_case(user_id=user.id, content=b"data", content_type="application/pdf")

    assert storage.objects == {}
    assert not uow.committed
