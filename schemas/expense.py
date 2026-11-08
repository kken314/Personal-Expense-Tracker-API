from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    date: date
    category_id: int

class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    date: date
    category_id: int

    model_config = ConfigDict(from_attributes=True)

class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    amount: Optional[float] = Field(default=None, gt=0)
    date: Optional[date] = None
    category_id: Optional[int] = None
