from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus


class OrderBase(BaseModel):
    total_amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: PaymentMethod = Field(default=PaymentMethod.COD)
    order_status: OrderStatus = Field(default=OrderStatus.PENDING)
    delivery_date: date | None = None
    delivery_fee: Decimal | None = None


class OrderRead(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)