from pydantic import BaseModel, computed_field ,ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime

class BrandBasic(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class CategoryBasic(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}

class BlobBasic(BaseModel):
    image_blob_url: Optional[str] = None
    model_config = {"from_attributes": True}

class ItemResponse(BaseModel):
    id: int
    name: str
    weight_kg: Optional[int] = None
    description: Optional[str] = None
    brand: BrandBasic
    category: CategoryBasic
    price: Decimal
    discount_price: Optional[Decimal] = None
    is_featured: bool
    current_stock: int
    blob: Optional[BlobBasic] = None
    created_at: datetime

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.current_stock > 0

    model_config = {"from_attributes": True}

class PaginatedItemsResponse(BaseModel):

    total: int
    page: int
    limit: int
    total_pages: int
    items: list[ItemResponse]

class ItemQueryParams(BaseModel):

    page: int = 1
    limit: int = 20
    search: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = True
    sort_by: str = "created_at"
    order: str = "desc"