from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.dependencies.services import get_brand_service
from app.services.brand_service import BrandService
from app.schemas.brand_schema import BrandResponse

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/search", response_model=list[BrandResponse])
def search_brands(
    brand_service: Annotated[BrandService, Depends(get_brand_service)],
    query: str = ""
):
    return brand_service.search_brands(query)
