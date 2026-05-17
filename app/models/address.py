from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from app.db.session import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(users.id),
        nullable=False
    )

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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="addresses"
    )