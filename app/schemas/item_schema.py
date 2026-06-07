from pydantic import BaseModel, computed_field ,ConfigDict,field_validator
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
    warranty_weeks: Optional[int]     = None
    brand: BrandBasic
    category: CategoryBasic
    price: Decimal
    discount_price: Optional[Decimal] = None
    is_featured: bool
    current_stock: int
    blob: Optional[BlobBasic] = None

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.current_stock > 0

    model_config = {"from_attributes": True}


class ItemAdminResponse(ItemResponse):
    cost_price: Optional[Decimal] = None  # profit info
    is_active:  bool
    created_at: datetime
    updated_at: datetime

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

class ItemCreateRequest(BaseModel):

    name:           str
    description:    Optional[str]     = None
    brand_id:       int
    category_id:    int
    price:          Decimal
    discount_price: Optional[Decimal] = None
    cost_price:     Optional[Decimal] = None
    warranty_weeks: Optional[int]     = None
    weight_kg:      Optional[Decimal] = None
    current_stock:  int
    is_featured:    bool              = False

    @field_validator("price", "cost_price", "discount_price")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Must be greater than 0")
        return v

    @field_validator("discount_price")
    @classmethod
    def discount_less_than_price(cls, v, info):
        price = info.data.get("price")
        if v is not None and price is not None and v >= price:
            raise ValueError("Discount price must be less than price")
        return v

    @field_validator("current_stock")
    @classmethod
    def stock_not_negative(cls, v):
        if v < 0:
            raise ValueError("Stock cannot be negative")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
    
class ItemUpdateRequest(BaseModel):
    name:           Optional[str]     = None
    description:    Optional[str]     = None
    brand_id:       Optional[int]     = None
    category_id:    Optional[int]     = None
    price:          Optional[Decimal] = None
    discount_price: Optional[Decimal] = None
    cost_price:     Optional[Decimal] = None
    warranty_weeks: Optional[int]     = None
    weight_kg:      Optional[Decimal] = None
    current_stock:  Optional[int]     = None
    is_featured:    Optional[bool]    = None
    is_active:      Optional[bool]    = None

    # ── Validators ────────────────────────────────────────────
    @field_validator("price", "cost_price", "discount_price")
    @classmethod
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Must be greater than 0")
        return v

    @field_validator("current_stock")
    @classmethod
    def stock_not_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Stock cannot be negative")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v