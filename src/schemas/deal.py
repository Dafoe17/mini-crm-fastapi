from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List, Union
from src.enums import DealStatus, ActionStatus


class DealBase(BaseModel):
    client_id: int = Field(gt=0)
    title: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    status: DealStatus
    value: int = Field(gt=0)
    created_at: datetime
    closed_at: datetime | None

    @field_validator("title")
    def strip_title(cls, v):
        return v.strip()

class DealRead(DealBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class DealCreate(DealBase):
    pass

class DealUpdate(DealBase):
    model_config = ConfigDict(partial=True)

class StatusDealsResponse(BaseModel):
    status: ActionStatus
    clients: Optional[Union[List[DealRead], DealRead]] = None
    details: Optional[str] = None

class DealsListResponse(BaseModel):
    total: int = Field(ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    clients: Optional[Union[List[DealRead], DealRead]] = None
