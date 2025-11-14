from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from typing import Optional, List, Union
from src.enums import DealStatus, ActionStatus


class DealBase(BaseModel):
    title: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    status: DealStatus
    value: int = Field(gt=0)
    closed_at: datetime | None = None

    @field_validator("title")
    def strip_title(cls, v):
        return v.strip()
    
    @field_validator("closed_at")
    def closed_at_not_in_past(cls, value):
        if value is None:
            return value

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        if value <= datetime.now(timezone.utc):
            raise ValueError("closed_at must be in the future")
        return value

class DealRead(DealBase):
    created_at: datetime
    updated_at: datetime
    id: int

    model_config = ConfigDict(from_attributes=True)

class DealCreate(DealBase):
    client_name: Optional[str] = None

class DealUpdate(DealBase):
    model_config = ConfigDict(partial=True)

class StatusDealsResponse(BaseModel):
    status: ActionStatus
    deals: Optional[Union[List[DealRead], DealRead]] = None
    details: Optional[str] = None

class DealsListResponse(BaseModel):
    total: int = Field(ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    deals: Optional[Union[List[DealRead], DealRead]] = None
