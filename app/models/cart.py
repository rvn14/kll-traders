from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from sqlalchemy import DateTime, Numeric, String, Text, UniqueConstraint, func, ForeignKey, Boolean, Integer

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.user import CustomerProfile

class Cart(Base):
    __tablename__ = "carts"

    id:Mapped[int] = mapped_column(primary_key=True)

    customer_id:Mapped[int] = mapped_column(ForeignKey("customer_profiles.id"),unique=True,nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    items:Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")

    customer:Mapped["CustomerProfile"] = relationship(back_populates="cart")

