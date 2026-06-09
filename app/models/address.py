from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship
from sqlalchemy import func
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.db.session import Base
from datetime import datetime

from app.models.user import CustomerProfile
from app.models.order_address import order_addresses

if TYPE_CHECKING:
    from app.models.order import Order


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_profile_id: Mapped[int] = mapped_column(ForeignKey("customer_profiles.id", ondelete="CASCADE"))

    address_line_1: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    
    address_line_2: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    city: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    postal_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    label: Mapped[str] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    customer_profile: Mapped["CustomerProfile"] = relationship(back_populates="addresses")

    delivery_orders: Mapped[list["Order"]] = relationship(
        back_populates="delivery_address",
        foreign_keys="Order.delivery_address_id",
    )

    orders: Mapped[list["Order"]] = relationship(
        secondary=order_addresses,
        back_populates="addresses",
    )