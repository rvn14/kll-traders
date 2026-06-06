from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.cart_schema import CartRead
from app.schemas.order_schema import OrderRead
from app.schemas.user_schema import UserBase, UserRead


class CustomerProfileRead(UserRead):
    addresses: list["AddressRead"] = []
    cart: CartRead | None = None
    orders: list["OrderRead"] = [] 

    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone_number: str | None = Field(default=None, min_length=10, max_length=20)

class AddressBase(BaseModel):
    address_line_1: str = Field(..., max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str = Field(..., max_length=255)
    postal_code: str = Field(..., max_length=20)
    label: str | None = Field(default=None, max_length=50)

class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    address_line_1: str | None = Field(default=None, max_length=255)
    address_line_2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=255)
    postal_code: str | None = Field(default=None, max_length=20)
    label: str | None = Field(default=None, max_length=50)

class AddressRead(AddressBase):
    id: int
    customer_profile_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)