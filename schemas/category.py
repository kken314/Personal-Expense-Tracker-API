from pydantic import BaseModel, ConfigDict, Field

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1)

class CategoryUpdate(BaseModel):
    name: str = Field(..., min_length=1)

class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
