from dataclasses import dataclass
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.platform.config import get_settings

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class Principal:
    issuer: str
    subject: str


@lru_cache
def jwks_client(url: str) -> PyJWKClient:
    # URL comes only from trusted deployment configuration, never token jku/x5u fields.
    return PyJWKClient(url, cache_keys=True, lifespan=300, timeout=5)


def authenticate(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> Principal:
    if credentials is None:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate": "Bearer"})
    settings = get_settings()
    try:
        if settings.auth_mode == "development":
            assert settings.dev_signing_secret is not None
            claims = jwt.decode(
                credentials.credentials,
                settings.dev_signing_secret.get_secret_value(),
                algorithms=["HS256"],
                issuer="growthpilot-local",
                audience="growthpilot-api",
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )
        else:
            key = jwks_client(settings.oidc_jwks_url).get_signing_key_from_jwt(
                credentials.credentials
            )
            claims = jwt.decode(
                credentials.credentials,
                key.key,
                algorithms=["RS256"],
                issuer=settings.oidc_issuer,
                audience=settings.oidc_audience,
                options={"require": ["exp", "iat", "sub", "iss", "aud"]},
            )
        if not isinstance(claims["sub"], str) or not claims["sub"]:
            raise ValueError("Invalid subject")
        return Principal(issuer=claims["iss"], subject=claims["sub"])
    except (jwt.PyJWTError, ValueError) as exc:
        raise HTTPException(401, "Invalid or expired credentials") from exc
