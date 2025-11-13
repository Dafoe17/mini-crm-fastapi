from pydantic import BaseModel, ConfigDict, StringConstraints, EmailStr, Field
from typing import Optional, List, Annotated, Union
from src.enums import ActionStatus

PhoneStr = Annotated[str, StringConstraints(pattern=r"^\+?(7|8)\d{10}$")]

class ClientBase(BaseModel):
    name: str = Field(max_length=50, min_length=2, strip_whitespace=True)
    email: EmailStr
    phone: PhoneStr
    notes: Optional[str] = Field(default="")

class ClientRead(ClientBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class ClientCreate(ClientBase):
    user_name: Optional[str] = None

class ClientUpdate(ClientBase):
    model_config = ConfigDict(partial=True)

class StatusClientsResponse(BaseModel):
    status: ActionStatus
    clients: Optional[Union[List[ClientRead], ClientRead]] = None
    details: Optional[str] = None

class ClientsListResponse(BaseModel):
    total: int = Field(ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    clients: Union[List[ClientRead], ClientRead]
