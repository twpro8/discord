from typing import cast

from src.core.storage import Storage


class FakeStorage:
    """In-memory stand-in for R2 used by integration tests. Only the methods
    the avatar flow touches are exercised."""

    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        self.objects[key] = data

    async def download_bytes(self, key: str) -> bytes:
        return self.objects[key]

    async def delete(self, key: str) -> None:
        self.objects.pop(key, None)

    def presigned_upload_url(
        self, key: str, content_type: str | None = None, expires_in: int = 900
    ) -> str:
        return f"https://files.example.com/{key}?presigned=1"

    def public_url(self, key: str) -> str:
        return f"https://files.example.com/{key}"


fake_storage = FakeStorage()


def get_test_storage() -> Storage | None:
    return cast(Storage | None, fake_storage)
