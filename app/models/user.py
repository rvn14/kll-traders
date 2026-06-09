from typing import TYPE_CHECKING

import enum
from sqlalchemy import UniqueConstraint
from app.db.session import Base
from sqlalchemy.orm import Mapped, mapped_column , relationship
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, func

from datetime import datetime

if TYPE_CHECKING:
    from app.models.address import Address
    from app.models.cart import Cart
    from app.models.order import Order


class UserRole(str,enum.Enum):
    ADMIN    = "admin"
    CUSTOMER = "customer"

class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    
    full_name: Mapped[str] = mapped_column(String(255),nullable=False)

    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    
    email: Mapped[str] = mapped_column( String(100),nullable=False,index=True )

    auth_provider: Mapped[AuthProvider] = mapped_column(
        Enum(AuthProvider, native_enum=False),
        default=AuthProvider.LOCAL,
        nullable=False
    )
    
    phone_number: Mapped[str] = mapped_column( String(20), nullable=True,)
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.CUSTOMER,
        nullable=False
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

    admin_profile: Mapped["AdminProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    customer_profile: Mapped["CustomerProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")

    @property
    def cart(self):
        return self.customer_profile.cart if self.customer_profile else None
        
    @property
    def addresses(self):
        return self.customer_profile.addresses if self.customer_profile else []
        
    @property
    def orders(self):
        return self.customer_profile.orders if self.customer_profile else []


class AdminProfile(Base):
    __tablename__ = "admin_profiles"

    id: Mapped[int] = mapped_column(primary_key=True , index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    user: Mapped["User"] = relationship(back_populates="admin_profile")


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    user: Mapped["User"] = relationship(back_populates="customer_profile")

    addresses: Mapped[list["Address"]] = relationship(back_populates="customer_profile" , cascade="all, delete-orphan" )

    cart: Mapped["Cart"] = relationship(back_populates="customer", uselist=False, cascade="all, delete-orphan")

    orders: Mapped[list["Order"]] = relationship(back_populates="customer", cascade="all, delete-orphan")

