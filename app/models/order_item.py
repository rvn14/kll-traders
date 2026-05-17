from sqlalchemy.orm import relationship
from decimal import Decimal
from datetime import datetime

from sqlalchemy import UniqueConstraint, ForeignKey, Numeric, String, DateTime, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "item_id", name="uq_order_item_order_id_item_id"),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False
    )

    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id"),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    warranty_weeks: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    order: Mapped["Order"] = relationship(
        back_populates="order_items"
    )

    item: Mapped["Item"] = relationship(
        back_populates="order_items"
    )