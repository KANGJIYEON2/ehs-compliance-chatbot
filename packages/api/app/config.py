from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database — EHS_DATABASE_URL to avoid collision with system DATABASE_URL
    EHS_DATABASE_URL: str = "sqlite:///./ehs.db"

    # Auth / JWT
    JWT_SECRET_KEY: str = "change-me-in-production"

    def validate_jwt_secret(self) -> None:
        insecure_defaults = ("change-me-in-production", "dev-secret-key-change-in-production")
        # 약한 시크릿(짧은 길이 포함)도 거부 — HS256 은 시크릿 엔트로피가 곧 보안.
        if self.JWT_SECRET_KEY in insecure_defaults or len(self.JWT_SECRET_KEY) < 32:
            import warnings
            warnings.warn(
                "JWT_SECRET_KEY is insecure (default or <32 chars). "
                "Set a strong random secret (e.g. `openssl rand -hex 32`) via environment variable.",
                stacklevel=2,
            )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OpenAI (existing)
    OPENAI_API_KEY: str = ""
    OPENAI_TIMEOUT: float = 90.0
    EHS_DB_DIRS: str = "vector_db_law,vector_db_rule"

    # Law API (국가법령정보센터)
    LAW_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: str = "*"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# packages/api/ 디렉토리 (벡터 DB, extracted_rule 등이 위치한 곳)
API_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


@lru_cache
def get_settings() -> Settings:
    return Settings()
