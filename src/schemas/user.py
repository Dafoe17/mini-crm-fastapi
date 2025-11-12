from pydantic import BaseModel, ConfigDict, Field, field_validator
from src.enums import UserRole
from src.core.security import hash_password
from typing import List
import re

PASSWORD_REGEX = {
    "letter": r"[a-zA-Z]",
    "digit": r"[0-9]",
    "special": r"[!.,_]"
}

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
        return hash_password(value)

class UserUpdate(UserCreate):

    model_config = ConfigDict(partial=True)

class StatusUsersResponse(BaseModel):
    status: str
    users: List[UserRead]

class UsersListResponse(BaseModel):
    total: int
    skip: int | None
    limit: int | None
    users: List[UserRead]
