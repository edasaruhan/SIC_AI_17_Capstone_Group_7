"""Private immutable objects; keys are derived from trusted UUIDs, never filenames."""

import os
from functools import lru_cache
from typing import Protocol
from uuid import UUID

import boto3

from app.platform.config import Settings, get_settings
from app.platform.errors import DomainError


class ObjectStore(Protocol):
    def put(self, tenant_id: UUID, object_id: UUID, content: bytes) -> None: ...

    def get(self, tenant_id: UUID, object_id: UUID, max_bytes: int) -> bytes: ...


class FileObjectStore:
    def __init__(self, settings: Settings) -> None:
        self.root = settings.object_root.resolve()

    def put(self, tenant_id: UUID, object_id: UUID, content: bytes) -> None:
        directory = self.root / str(tenant_id)
        directory.mkdir(parents=True, mode=0o700, exist_ok=True)
        descriptor = os.open(
            directory / str(object_id), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600
        )
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)

    def get(self, tenant_id: UUID, object_id: UUID, max_bytes: int) -> bytes:
        with (self.root / str(tenant_id) / str(object_id)).open("rb") as source:
            content = source.read(max_bytes + 1)
        if len(content) > max_bytes:
            raise DomainError("Stored object exceeds read limit", 413)
        return content


class S3ObjectStore:
    def __init__(self, settings: Settings) -> None:
        self.bucket = settings.s3_bucket
        self.client = boto3.client("s3", endpoint_url=settings.s3_endpoint)

    def put(self, tenant_id: UUID, object_id: UUID, content: bytes) -> None:
        self.client.put_object(
            Bucket=self.bucket,
            Key=f"{tenant_id}/{object_id}",
            Body=content,
            ContentType="application/octet-stream",
            ServerSideEncryption="AES256",
            IfNoneMatch="*",
        )

    def get(self, tenant_id: UUID, object_id: UUID, max_bytes: int) -> bytes:
        response = self.client.get_object(Bucket=self.bucket, Key=f"{tenant_id}/{object_id}")
        body = response["Body"]
        try:
            content = body.read(max_bytes + 1)
        finally:
            body.close()
        if len(content) > max_bytes:
            raise DomainError("Stored object exceeds read limit", 413)
        return content


@lru_cache
def get_object_store() -> ObjectStore:
    settings = get_settings()
    return S3ObjectStore(settings) if settings.object_backend == "s3" else FileObjectStore(settings)
