from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.dependencies.services import get_category_service
from app.services.category_service import CategoryService
from app.schemas.category_schema import CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get("", response_model=list[CategoryResponse])
def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)]
):
    return category_service.get_categories()
