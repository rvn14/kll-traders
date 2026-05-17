from sqlalchemy import UniqueConstraint

from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Numeric, String, Text, UniqueConstraint, func

from datetime import datetime

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    
    phone_number: Mapped[str] = mapped_column(
        String(20),
        nullable=True,
    )
    
    address: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    
    is_active: Mapped[bool] = mapped_column(
        nullable=False,
        default=True,
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
