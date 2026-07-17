from decimal import Decimal

from fastapi import HTTPException, status

from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository):
        self.settings_repository = settings_repository

    def get_tax_rate(self) -> Decimal:
        return self.settings_repository.get_tax_rate()

    def update_tax_rate(self, rate: Decimal) -> Decimal:
        if rate < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tax rate cannot be negative",
            )
        self.settings_repository.upsert_setting(
            "tax_rate_percent", str(rate)
        )
        return rate
