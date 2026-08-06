from src.core.storage import R2Storage


class _DummyClient:
    """Stand-in for the aiobotocore client; the methods under test never
    touch it."""


def _make_storage() -> R2Storage:
    return R2Storage(
        _DummyClient(),  # type: ignore[arg-type]
        bucket="lumiere-uploads",
        public_base_url="https://pub-abc123.r2.dev/",
    )


def test_public_url_strips_trailing_slash_from_base() -> None:
    storage = _make_storage()
    assert storage.public_url("attachments/abc.png") == (
        "https://pub-abc123.r2.dev/attachments/abc.png"
    )


def test_public_url_uses_plain_base_when_no_trailing_slash() -> None:
    storage = R2Storage(
        _DummyClient(),  # type: ignore[arg-type]
        bucket="lumiere-uploads",
        public_base_url="https://files.example.com",
    )
    assert storage.public_url("chat/1/msg/2.png") == (
        "https://files.example.com/chat/1/msg/2.png"
    )
