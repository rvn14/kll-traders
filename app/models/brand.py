from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.blobs import Blob
from app.models.item import Item

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

    blob: Mapped["Blob"] = relationship(
        back_populates="brand"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    items: Mapped[list["Item"]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
    