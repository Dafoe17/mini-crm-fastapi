from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime, timezone
from src.enums import TaskStatus, ActionStatus
from typing import Optional, Union, List


class TaskBase(BaseModel):
    title: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    description: Optional[str] = Field(default="", max_length=200, json_schema_extra={"strip_whitespace": True}) 
    due_date: datetime | None = None
    status: TaskStatus

    @field_validator("title")
    def strip_title(cls, v):
        return v.strip()
    
    @field_validator("description")
    def strip_description(cls, v):
        return v.strip()
    
    @field_validator("due_date")
    def due_date_not_in_past(cls, value):
        if value is None:
            return value

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        if value <= datetime.now(timezone.utc):
            raise ValueError("due_date must be in the future")
        return value

class TaskRead(TaskBase):
    created_at: datetime
    updated_at: datetime
    id: int

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    user_name: Optional[str] = None

class TaskUpdate(TaskBase):
    model_config = ConfigDict(partial=True)

class StatusTasksResponse(BaseModel):
    status: ActionStatus
    clients: Optional[Union[List[TaskRead], TaskRead]] = None
    tasks: Optional[str] = None

class TasksListResponse(BaseModel):
    total: int = Field(ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    tasks: Optional[Union[List[TaskRead], TaskRead]] = None
