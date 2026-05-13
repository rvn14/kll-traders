from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

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
    
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
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