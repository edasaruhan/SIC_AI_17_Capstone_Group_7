import hashlib
import hmac

from app.platform.rate_limit import allow_request, protected_rate_key
from app.platform.webhooks import verify_sha256_signature
from conftest import auth_headers
from fastapi.testclient import TestClient


class Counter:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.expirations: list[tuple[str, int]] = []

    def incr(self, key: str) -> int:
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    def expire(self, key: str, seconds: int) -> None:
        self.expirations.append((key, seconds))


def test_webhook_signature_is_constant_format_and_tamper_sensitive() -> None:
    body, secret = b'{"event":"sync"}', "synthetic-secret-value"
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    assert verify_sha256_signature(body, signature, secret)
    assert not verify_sha256_signature(body + b"x", signature, secret)
    assert not verify_sha256_signature(body, "bad", secret)


def test_rate_key_hides_subject_and_enforces_limit() -> None:
    key = protected_rate_key("gp", "assistant", "raw-user-identifier", 123)
    assert "raw-user-identifier" not in key
    store = Counter()
    assert allow_request(store, key, limit=2, window_seconds=60)
    assert allow_request(store, key, limit=2, window_seconds=60)
    assert not allow_request(store, key, limit=2, window_seconds=60)
    assert store.expirations == [(key, 60)]


def test_security_headers_and_tenant_audit_visibility(
    client: TestClient, tenants: dict[str, dict[str, object]]
) -> None:
    response = client.get("/api/v1/workspace", headers=auth_headers(tenants["a"]))
    assert response.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    audit = client.get("/api/v1/audit", headers=auth_headers(tenants["a"]))
    assert audit.status_code == 200
    other = client.get("/api/v1/audit", headers=auth_headers(tenants["b"]))
    assert all(row["actor_id"] != str(tenants["a"]["actor"]) for row in other.json())
    analyst = client.get("/api/v1/audit", headers=auth_headers(tenants["analyst"]))
    assert analyst.status_code == 403
