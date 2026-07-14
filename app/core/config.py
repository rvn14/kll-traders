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

    # Delivery fee settings
    STORE_CITY: str = "Colombo"
    DELIVERY_FEE_LOCAL: float = 0
    DELIVERY_FEE_NEARBY: float = 500
    DELIVERY_FEE_OTHER: float = 1000
    NEARBY_CITIES: str = ""  # comma-separated, e.g. "Negombo,Gampaha,Kalutara"

    # Default tax rate (fallback if DB has no entry)
    DEFAULT_TAX_RATE_PERCENT: float = 3.0

    # Cart history limit (max past items to keep in cart)
    CART_HISTORY_LIMIT: int = 50

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

    def get_nearby_cities_list(self) -> list[str]:
        if not self.NEARBY_CITIES:
            return []
        return [c.strip().lower() for c in self.NEARBY_CITIES.split(",") if c.strip()]
    
@lru_cache()
def get_settings() -> Settings:
    return Settings()
