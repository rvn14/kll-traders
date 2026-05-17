from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship , ForeignKey

from app.db.session import Base
from app.models.brand import Brand
from app.models.item import Item

class Blob(Base):
    __tablename__ = "blobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    image_blob_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_blob_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("brands.id"),
        nullable=True
    )

    brand: Mapped["Brand"] = relationship(
        back_populates="blob"
    )

    item_id: Mapped[int | None] = mapped_column(
        ForeignKey("items.id"),
        nullable=True
    )

    item: Mapped["Item"] = relationship(
        back_populates="blob"
    )