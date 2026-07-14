from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, OrderType, PaymentMethod, PaymentStatus
from app.schemas.cutomer_profile_schema import AddressRead


# Request Schemas 

class CheckoutFromCartRequest(BaseModel):
    order_type: OrderType
    delivery_address_id: int | None = None
    order_note: str | None = None


class DirectBuyRequest(BaseModel):
    item_id: int
    quantity: int = Field(..., ge=1)
    order_type: OrderType
    delivery_address_id: int | None = None
    order_note: str | None = None


class AdminOrderUpdateRequest(BaseModel):
    delivery_address_id: int | None = None
    order_note: str | None = None


class AdminOrderStatusUpdate(BaseModel):
    order_status: OrderStatus | None = None
    payment_status: PaymentStatus | None = None


class TaxRateUpdate(BaseModel):
    rate: Decimal = Field(..., ge=0)


# Response Schemas


class TaxRateRead(BaseModel):
    rate: Decimal


class OrderItemRead(BaseModel):
    id: int
    item_id: int
    item_name: str
    quantity: int
    unit_price: Decimal
    discount_price: Decimal | None = None
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class BillSummary(BaseModel):
    order_id: int
    invoice_no: str
    order_type: OrderType
    order_status: OrderStatus
    payment_status: PaymentStatus
    items: list[OrderItemRead] = []
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    delivery_address: AddressRead | None = None
    order_note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    invoice_no: str
    customer_id: int
    order_type: OrderType
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    order_status: OrderStatus
    delivery_date: date | None = None
    order_note: str | None = None
    delivery_address: AddressRead | None = None
    order_items: list[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedOrdersResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    orders: list[OrderRead]


class PurchasedItemRead(BaseModel):
    order_item_id: int
    item_id: int
    item_name: str
    item_image: str | None = None
    quantity: int
    unit_price: Decimal
    discount_price: Decimal | None = None
    line_total: Decimal
    purchased_at: datetime
    invoice_no: str


class PaginatedPurchaseHistory(BaseModel):
    total: int
    page: int
    limit: int
    items: list[PurchasedItemRead]