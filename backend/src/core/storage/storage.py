from contextlib import AbstractAsyncContextManager
from typing import Protocol, cast

from botocore.client import BaseClient

from src.core.logging import get_logger

logger = get_logger(__name__)


class Storage(Protocol):
    """Abstract object-storage contract. Modules depend on this, not on
    aiobotocore directly — swapping R2 for another S3-compatible provider
    (or a local MinIO) later touches only R2Storage, not any handler.
    """

    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None: ...

    async def download_bytes(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> None: ...

    def presigned_upload_url(
        self, key: str, content_type: str | None = None, expires_in: int = 900
    ) -> str: ...

    def public_url(self, key: str) -> str: ...


class R2Storage:
    """S3-compatible Cloudflare R2 storage backed by one long-lived
    aiobotocore client. Presigned URLs are generated synchronously
    (botocore signing) and don't touch the network.
    """

    def __init__(
        self,
        client: BaseClient,
        bucket: str,
        public_base_url: str,
        client_context: AbstractAsyncContextManager[BaseClient] | None = None,
    ) -> None:
        self._client = client
        self._client_context = client_context
        self._bucket = bucket
        self._public_base_url = public_base_url.rstrip("/")

    async def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        await self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            **({"ContentType": content_type} if content_type else {}),
            **({"Metadata": metadata} if metadata else {}),
        )

    async def download_bytes(self, key: str) -> bytes:
        response = await self._client.get_object(Bucket=self._bucket, Key=key)
        body = await response["Body"].read()
        return cast(bytes, body)

    async def delete(self, key: str) -> None:
        await self._client.delete_object(Bucket=self._bucket, Key=key)

    def presigned_upload_url(
        self, key: str, content_type: str | None = None, expires_in: int = 900
    ) -> str:
        params = {"Bucket": self._bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        url = self._client.generate_presigned_url(
            "put_object", Params=params, ExpiresIn=expires_in
        )
        return cast(str, url)

    def public_url(self, key: str) -> str:
        return f"{self._public_base_url}/{key}"

    async def close(self) -> None:
        if self._client_context is not None:
            await self._client_context.__aexit__(None, None, None)
            self._client_context = None
            return
        await self._client.close()
