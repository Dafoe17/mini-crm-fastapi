from pydantic import BaseModel, ConfigDict, Field, StringConstraints, EmailStr, field_validator
from datetime import datetime
from typing import Optional, Annotated
from src.enums import DealStatus, TaskStatus, UserRole
import re

PhoneStr = Annotated[str, StringConstraints(pattern=r"^\+?[()\d\s-]{7,20}$")]

PASSWORD_REGEX = {
    "letter": r"[a-zA-Z]",
    "digit": r"[0-9]",
    "special": r"[!.,_]"
}

# for use without pydantic.EmailStr:
# email_patter = ^[\w_.+-]+@[\w\d-]+\.[\w\d-]{2,}$

# --Users--

class UserBase(BaseModel):
    username: str = Field(max_length=50, min_length=2, strip_whitespace=True)
    role: UserRole

class UserRead(UserBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(strip_whitespace=True)

    @field_validator('password')
    def password_strength_check(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not re.search(PASSWORD_REGEX["letter"], value):
            raise ValueError("Password must contain at least one letter")
        if not re.search(PASSWORD_REGEX["digit"], value):
            raise ValueError("Password must contain at least one number")
        if not re.search(PASSWORD_REGEX["special"], value):
            raise ValueError("Password must contain at least one special symbols (!.,_)")
        return value

class UserUpdate(UserBase):
    model_config = ConfigDict(partial=True)
    password: Optional[str] = Field(default=None, max_length=50, min_length=6, strip_whitespace=True)

# --Clients--

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


# --Deals--

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


# --Tasks--

class TaskBase(BaseModel):
    deal_id: int = Field(gt=0)
    title: str = Field(max_length=50, min_length=2, strip_whitespace=True)
    description: Optional[str] = Field(default="", max_length=200, strip_whitespace=True) 
    due_date: datetime | None
    status: TaskStatus

class TaskRead(TaskBase):
    id: int
    deal: DealRead

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    model_config = ConfigDict(partial=True)
