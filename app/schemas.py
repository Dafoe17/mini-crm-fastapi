from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from enums import DealStatus, TaskStatus

# --Users--

class UserBase(BaseModel):
    username: str
    password_hash: str

class UserRead(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    pass

# --Clients--

class ClientBase(BaseModel):
    user_id: int = Field(gt=0)
    name: str
    email: str
    phone: str
    notes: str

class ClientRead(ClientBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class ClientCreate(ClientBase):
    pass

# --Deals--

class DealBase(BaseModel):
    client_id: int = Field(gt=0)
    title: str
    status: DealStatus
    value: int
    created_at: datetime
    closed_at: Optional[datetime] = None

class DealRead(DealBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class DealCreate(DealBase):
    pass

# --Tasks--

class TaskBase(BaseModel):
    deal_id: int = Field(gt=0)
    title: str
    description: str
    due_date: datetime
    status: TaskStatus

class TaskRead(TaskBase):
    id: int
    deal: DealRead

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    pass
