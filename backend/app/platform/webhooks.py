import hashlib
import hmac


def verify_sha256_signature(body: bytes, header: str, secret: str) -> bool:
    if not header.startswith("sha256=") or len(secret) < 16:
        return False
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header)
