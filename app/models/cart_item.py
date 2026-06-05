from __future__ import annotations
from typing import TYPE_CHECKING

from app.db.session import Base
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.item import Item

class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "item_id", name="uq_cart_item"),
    )

    id:Mapped[int] = mapped_column(primary_key=True)

    cart_id:Mapped[int] = mapped_column(ForeignKey("carts.id",ondelete="CASCADE"))

    item_id:Mapped[int] = mapped_column(ForeignKey("items.id",ondelete="CASCADE"))

    quantity:Mapped[int]   = mapped_column(Integer, default=1)

    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cart:Mapped["Cart"] = relationship(back_populates="items")

    item:Mapped["Item"] = relationship(back_populates="cart_items")