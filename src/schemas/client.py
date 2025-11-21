from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List, Union
from src.enums import ActionStatus

class ClientBase(BaseModel):
    name: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    email: Optional[EmailStr] = Field(default="")
    phone: Optional[str] = Field(default="")
    notes: Optional[str] = Field(default="")

    @field_validator("name")
    def strip_name(cls, v):
        return v.strip()
    
class ClientRead(ClientBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class ClientCreate(ClientBase):
    user_name: Optional[str] = None

class StatusClientsResponse(BaseModel):
    status: ActionStatus
    clients: Optional[Union[List[ClientRead], ClientRead]] = None

class ClientsListResponse(BaseModel):
    total: int = Field(ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    clients: Optional[Union[List[ClientRead], ClientRead]] = None
