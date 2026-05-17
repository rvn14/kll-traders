from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    logo_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    website_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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

    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="brand"
    )