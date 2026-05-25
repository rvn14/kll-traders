 from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

class CustomerBase(BaseModel):
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Full name of the customer",
        
    )
    
    email: EmailStr = Field(
        ...,
        min_length=5,
        max_length=255,
        description="Email address of the customer",
    )
    
    phone_number: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Phone number of the customer",
    )
    
    address: str | None = Field(
        default=None,
        max_length=500,
        description="Address of the customer",
    )
    
    
class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Updated full name of the customer",
    )
    
    email: EmailStr | None = Field(
        default=None,
        min_length=5,
        max_length=255,
        description="Updated email address of the customer",
    )
    
    phone_number: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Updated phone number of the customer",
    )
    
    is_active: bool | None = Field(
        default=None,
        description="Updated active status of the customer",
    )   
    
    address: str | None = Field(
        default=None,
        max_length=500,
        description="Updated address of the customer",
    )
    
class CustomerRead(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)