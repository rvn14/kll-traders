from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item_schema import ItemResponse


class CartItemRead(BaseModel):
    id: int
    cart_id: int
    item_id: int
    quantity: int
    is_selected: bool
    added_at: datetime

    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)

class CartRead(BaseModel):
    id: int
    customer_id: int
    updated_at: datetime
    
    items: list[CartItemRead] = []
    
    model_config = ConfigDict(from_attributes=True)


class CartItemAdd(BaseModel):
    item_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemSelect(BaseModel):
    is_selected: bool