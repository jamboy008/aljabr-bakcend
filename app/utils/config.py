from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    SECRET_KEY: str = Field(min_length=32)
    DATABASE_URL: str | None = None
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USERNAME: str = "aljabr"
    DB_PASS: str = ""
    DB_NAME: str = "aljabr"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "testserver"]
    RATE_LIMIT_STORAGE: str = "memory://"
    DOCS_ENABLED: bool = True
    ACCESS_TOKEN_MINUTES: int = Field(default=16, ge=1, le=60)
    REFRESH_TOKEN_DAYS: int = Field(default=3, ge=1, le=30)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def secure_secret(cls, value):
        if value.startswith("replace-"):
            raise ValueError("Set a randomly generated SECRET_KEY")
        return value


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()