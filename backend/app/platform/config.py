from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GP_", env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "production"
    auth_mode: Literal["development", "oidc"] = "oidc"
    database_url: SecretStr
    migration_database_url: SecretStr | None = None
    dev_signing_secret: SecretStr | None = None
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    allowed_origins: list[str] = []
    redis_url: SecretStr = SecretStr("redis://127.0.0.1:56379/0")
    redis_namespace: str = "growthpilot"
    object_root: Path = Path(".local/objects")
    object_backend: Literal["filesystem", "s3"] = "filesystem"
    s3_bucket: str = ""
    s3_endpoint: str | None = None
    max_upload_bytes: int = 5 * 1024 * 1024
    model_path: Path = Path(".local/models/final_candidate.joblib")
    model_manifest_path: Path = Path("artifacts/ml/final_candidate.json")
    experimental_scoring_demo_only: bool = True
    identifier_hmac_secret: SecretStr | None = None
    marketing_kill_switch: bool = True
    max_campaign_budget: float = 0.0
    llm_provider: Literal["disabled", "openai_compatible"] = "disabled"
    llm_api_key: SecretStr | None = None
    llm_model: str = ""

    @model_validator(mode="after")
    def validate_auth(self) -> "Settings":
        if self.object_backend == "s3" and not self.s3_bucket:
            raise ValueError("S3 bucket is required")
        if self.auth_mode == "development":
            if self.environment == "production":
                raise ValueError("Development authentication is forbidden in production")
            if not self.dev_signing_secret or len(self.dev_signing_secret.get_secret_value()) < 32:
                raise ValueError(
                    "Development authentication requires a random local signing secret"
                )
        elif not (
            self.oidc_issuer.startswith("https://")
            and self.oidc_audience
            and self.oidc_jwks_url.startswith("https://")
        ):
            raise ValueError("OIDC issuer, audience and trusted HTTPS JWKS URL are required")
        if "*" in self.allowed_origins:
            raise ValueError("Wildcard CORS origins are not supported")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
