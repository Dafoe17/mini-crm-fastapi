from pydantic import BaseModel, ConfigDict, StringConstraints, EmailStr, Field
from typing import Optional, Annotated


PhoneStr = Annotated[str, StringConstraints(pattern=r"^\+?[()\d\s-]{7,20}$")]

class ClientBase(BaseModel):
    user_id: int = Field(gt=0)
    name: str = Field(max_length=50, min_length=2, strip_whitespace=True)
    email: EmailStr
    phone: PhoneStr
    notes: Optional[str] = Field(default="")

class ClientRead(ClientBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(ClientBase):
    model_config = ConfigDict(partial=True)
