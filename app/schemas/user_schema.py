from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole

class UserBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Full name of the user",
        
    )
    
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Email address of the customer",
    )
    
    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Phone number of the customer",
    )

    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="Role of the user, either 'customer' or 'admin'",
    )
    
    
class UserCreate(UserBase):
    password: str | None = Field(
        ..., 
        min_length=8, 
        max_length=120,
        description="Password for the customer account",
    )


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Updated full name of the user",
    )
    
    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Updated phone number of the user",
    )
    
    is_active: bool | None = Field(
        default=None,
        description="Updated active status of the user",
    )

    role: UserRole = Field(
        default=UserRole.CUSTOMER,
        description="Role of the user, either 'customer' or 'admin'",
    )
    

class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)