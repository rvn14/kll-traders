from functools import lru_cache

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Items CRUD API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://username:password@host/db"
    AZURE_STORAGE_CONNECTION_STRING: SecretStr | None = None
    AZURE_STORAGE_ACCOUNT_NAME: str | None = None
    AZURE_STORAGE_ACCOUNT_KEY: SecretStr | None = None
    AZURE_STORAGE_CONTAINER_NAME: str | None = None
    AZURE_BLOB_CONTAINER_NAME: str = "items"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized_value = value.strip().lower()
            if normalized_value in {"release", "prod", "production"}:
                return False

        return value
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()
