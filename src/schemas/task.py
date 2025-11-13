from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.schemas.deal import DealRead
from datetime import datetime
from src.enums import TaskStatus
from typing import Optional


class TaskBase(BaseModel):
    deal_id: int = Field(gt=0)
    title: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    description: Optional[str] = Field(default="", max_length=200, json_schema_extra={"strip_whitespace": True}) 
    due_date: datetime | None
    status: TaskStatus

    @field_validator("title")
    def strip_title(cls, v):
        return v.strip()
    
    @field_validator("description")
    def strip_description(cls, v):
        return v.strip()

class TaskRead(TaskBase):
    id: int
    deal: DealRead

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    model_config = ConfigDict(partial=True)
