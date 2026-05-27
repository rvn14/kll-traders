from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.item_schema import ItemResponse


class CartItemRead(BaseModel):
    id: int
    cart_id: int
    item_id: int
    quantity: int
    added_at: datetime

    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)

class CartRead(BaseModel):
    id: int
    customer_id: int
    updated_at: datetime
    
    items: list[CartItemRead] = []
    
    model_config = ConfigDict(from_attributes=True)