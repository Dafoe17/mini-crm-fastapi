from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.enums import UserRole, ActionStatus
from src.core.security import hash_password
from typing import Optional, Union, List
import re

PASSWORD_REGEX = {
    "letter": r"[a-zA-Z]",
    "digit": r"[0-9]",
    "special": r"[!.,_]"
}

class UserBase(BaseModel):
    username: str = Field(max_length=50, min_length=2, json_schema_extra={"strip_whitespace": True})
    role: UserRole

    @field_validator("username")
    def strip_username(cls, v):
        return v.strip()
    
class UserRead(UserBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str = Field(json_schema_extra={"strip_whitespace": True})

    @field_validator("password")
    def strip_password(cls, v):
        return v.strip()

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
        return hash_password(value)

class UserUpdate(UserCreate):

    model_config = ConfigDict(partial=True)

class StatusUsersResponse(BaseModel):
    status: ActionStatus 
    users: Optional[Union[List[UserRead], UserRead]] = None
    details: Optional[str] = None

class UsersListResponse(BaseModel):
    total: int = Field(default=0, ge=0)
    skip: Optional[int] = Field(default=None, ge=0)
    limit: Optional[int] = Field(default=None, ge=0)
    users: Optional[Union[List[UserRead], UserRead]] = None
