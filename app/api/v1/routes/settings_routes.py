from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.admin import require_admin
from app.api.dependencies.services import get_settings_service
from app.models.user import User
from app.schemas.order_schema import TaxRateRead, TaxRateUpdate
from app.services.settings_service import SettingsService

router = APIRouter(
    prefix="/admin/settings",
    tags=["Admin - Settings"],
)


@router.get(
    "/tax-rate",
    response_model=TaxRateRead,
    status_code=status.HTTP_200_OK,
)
def get_tax_rate(
    settings_service: Annotated[SettingsService, Depends(get_settings_service)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Get current tax rate."""
    rate = settings_service.get_tax_rate()
    return TaxRateRead(rate=rate)


@router.patch(
    "/tax-rate",
    response_model=TaxRateRead,
    status_code=status.HTTP_200_OK,
)
def update_tax_rate(
    payload: TaxRateUpdate,
    settings_service: Annotated[SettingsService, Depends(get_settings_service)],
    _admin: Annotated[User, Depends(require_admin)],
):
    """Update tax rate (admin only)."""
    rate = settings_service.update_tax_rate(payload.rate)
    return TaxRateRead(rate=rate)
