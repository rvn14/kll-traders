from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import ForeignKey, Numeric, String, DateTime, func, Enum, Text, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from app.db.session import Base

from app.models.order_address import order_addresses
from app.models.user import CustomerProfile

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.item import Item
    from app.models.order_item import OrderItem
    from app.models.user import User


def _create_order_item(item):
    from app.models.order_item import OrderItem
    return OrderItem(item=item)


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    COD = "cash-on-delivery"
    WHATSAPP = "whatsapp"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderType(str, enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    invoice_no: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer_profiles.id"),
        nullable=False
    )

    customer: Mapped["CustomerProfile"] = relationship(
        back_populates="orders"
    )

    order_type: Mapped[OrderType] = mapped_column(
        Enum(OrderType, native_enum=False),
        nullable=False,
        default=OrderType.DELIVERY,
    )

    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
    )

    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, native_enum=False),
        nullable=False,
        default=PaymentMethod.WHATSAPP,
    )

    order_status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
    )

    delivery_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    order_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    delivery_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("addresses.id"),
        nullable=True
    )

    delivery_address: Mapped["Address | None"] = relationship(
        foreign_keys=[delivery_address_id],
        back_populates="delivery_orders",
    )

    addresses: Mapped[list["Address"]] = relationship(
        secondary=order_addresses,
        back_populates="orders",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order"
    )

    items: AssociationProxy[list["Item"]] = association_proxy(
        "order_items",
        "item",
        creator=_create_order_item
    )
