from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.app_settings import AppSettings


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_setting(self, key: str) -> str | None:
        statement = select(AppSettings).where(AppSettings.key == key)
        setting = self.db.execute(statement).scalars().first()
        return setting.value if setting else None

    def upsert_setting(self, key: str, value: str) -> AppSettings:
        try:
            statement = select(AppSettings).where(AppSettings.key == key)
            setting = self.db.execute(statement).scalars().first()

            if setting is None:
                setting = AppSettings(key=key, value=value)
                self.db.add(setting)
            else:
                setting.value = value

            self.db.commit()
            self.db.refresh(setting)
            return setting
        except Exception:
            self.db.rollback()
            raise

    def get_tax_rate(self) -> Decimal:
        value = self.get_setting("tax_rate_percent")
        if value is None:
            return Decimal("3.0")
        return Decimal(value)
