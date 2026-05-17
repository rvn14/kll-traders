from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, UniqueConstraint, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from app.db.session import Base
from app.models.category import Category


def _create_order_item_from_item(order):
    from app.models.order_item import OrderItem
    return OrderItem(order=order)

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
    
    original_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    current_stock: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    low_stock_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    image_blob_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_blob_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="items"
    )

    brand: Mapped["Brand"] = relationship(
        "Brand",
        back_populates="items"
    )

    cart_item: Mapped["CartItem"] = relationship(
        back_populates="item"
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="item"
    )

    orders: AssociationProxy[list["Order"]] = association_proxy(
        "order_items",
        "order",
        creator=_create_order_item_from_item
    )

