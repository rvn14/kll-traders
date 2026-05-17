from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Numeric, String, Text, UniqueConstraint, func, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from __future__ import annotations
from typing import TYPE_CHECKING
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.blobs import Blob
    from app.models.brand import Brand
    from app.models.category import Category
    from app.models.cart_item import CartItem

class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("name", name="uq_item_name"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )

    brand_id: Mapped[int] = mapped_column(
        ForeignKey("brands.id"),
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )
    
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    ) 
    
    discount_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    ) 
    
    cost_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    current_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    blob: Mapped["Blob"] = relationship(
        back_populates="item"
    )

    category: Mapped["Category"] = relationship(
        back_populates="items"
    )

    brand: Mapped["Brand"] = relationship(
        back_populates="items"
    )

    cart_items:Mapped[list["CartItem"]] = relationship(back_populates="item")

