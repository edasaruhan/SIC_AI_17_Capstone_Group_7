import io
from uuid import uuid4

import boto3
import pytest
from app.platform.config import Settings
from app.platform.csv_export import safe_csv
from app.platform.storage import FileObjectStore, S3ObjectStore
from botocore.response import StreamingBody
from botocore.stub import Stubber


def test_filesystem_is_immutable_and_tenant_scoped(tmp_path) -> None:
    settings = Settings().model_copy(update={"object_root": tmp_path})
    store = FileObjectStore(settings)
    tenant, object_id = uuid4(), uuid4()
    store.put(tenant, object_id, b"raw-data")
    with pytest.raises(FileExistsError):
        store.put(tenant, object_id, b"changed")
    with pytest.raises(FileNotFoundError):
        store.get(uuid4(), object_id, 100)
    assert store.get(tenant, object_id, 100) == b"raw-data"
    assert (tmp_path / str(tenant) / str(object_id)).stat().st_mode & 0o777 == 0o600


def test_s3_contract_without_live_provider(monkeypatch) -> None:
    client = boto3.client(
        "s3",
        region_name="eu-west-1",
        aws_access_key_id="synthetic",
        aws_secret_access_key="synthetic",
    )
    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: client)
    store = S3ObjectStore(Settings().model_copy(update={"s3_bucket": "synthetic-bucket"}))
    tenant, object_id = uuid4(), uuid4()
    key = f"{tenant}/{object_id}"
    with Stubber(client) as stub:
        stub.add_response(
            "put_object",
            {},
            {
                "Bucket": "synthetic-bucket",
                "Key": key,
                "Body": b"source",
                "ContentType": "application/octet-stream",
                "ServerSideEncryption": "AES256",
                "IfNoneMatch": "*",
            },
        )
        store.put(tenant, object_id, b"source")
        stub.add_response(
            "get_object",
            {"Body": StreamingBody(io.BytesIO(b"source"), 6)},
            {"Bucket": "synthetic-bucket", "Key": key},
        )
        assert store.get(tenant, object_id, 100) == b"source"
        stub.assert_no_pending_responses()


def test_csv_formula_prefixes_are_neutralized() -> None:
    output = safe_csv([["=SUM(1)", "+123", "-1", "@X", "\t=1", "safe"]])
    assert output == "'=SUM(1),'+123,'-1,'@X,'\t=1,safe\r\n"
