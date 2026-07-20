from pydantic import BaseModel

class BrandResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
