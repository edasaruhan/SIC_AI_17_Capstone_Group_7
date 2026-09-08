import pytest
from app.identity.permissions import ROLE_PERMISSIONS, Permission
from app.platform.config import Settings
from pydantic import ValidationError


def test_production_rejects_development_auth() -> None:
    with pytest.raises(ValidationError, match="forbidden"):
        Settings(
            _env_file=None,
            environment="production",
            auth_mode="development",
            database_url="postgresql+psycopg://localhost/test",
            dev_signing_secret="x" * 40,
        )


def test_analyst_cannot_write_or_approve() -> None:
    assert ROLE_PERMISSIONS["ANALYST"] == {Permission.READ}
    assert Permission.APPROVE not in ROLE_PERMISSIONS["MARKETING_MANAGER"]


def test_production_needs_trusted_issuer() -> None:
    with pytest.raises(ValidationError, match="OIDC"):
        Settings(
            _env_file=None,
            database_url="postgresql+psycopg://localhost/test",
            environment="production",
            auth_mode="oidc",
        )
