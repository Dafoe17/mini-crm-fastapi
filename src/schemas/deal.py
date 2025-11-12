from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from src.enums import DealStatus


class DealBase(BaseModel):
    client_id: int = Field(gt=0)
    title: str = Field(max_length=50, min_length=2, strip_whitespace=True)
    status: DealStatus
    value: int = Field(gt=0)
    created_at: datetime
    closed_at: datetime | None

class DealRead(DealBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class DealCreate(DealBase):
    pass

class DealUpdate(DealBase):
    model_config = ConfigDict(partial=True)