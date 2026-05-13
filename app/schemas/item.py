from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Name of the item",
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional item description",
    )

    price: float = Field(
        ...,
        gt=0,
        le=99_999_999.99,
        multiple_of=0.01,
        description="Item price. Must be greater than 0.",
        examples=[175.00],
    )


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        description="Updated item name",
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Updated item description",
    )

    price: float | None = Field(
        default=None,
        gt=0,
        le=99_999_999.99,
        multiple_of=0.01,
        description="Updated item price",
        examples=[175.00],
    )


class ItemRead(ItemBase):
    id: int
    image_blob_url: str | None = None
    image_blob_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
