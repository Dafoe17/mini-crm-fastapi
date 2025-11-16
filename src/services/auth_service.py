from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.repositories.users_repository import UsersRepository
from src.core.security import (
    verify_password,
    create_access_token,
    hash_password
)

class AuthService:

    @staticmethod
    def login(db: Session, username: str, password: str):
        user = UsersRepository.get_by_username(db, username)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({
            "sub": user.username,
            "role": user.role
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    @staticmethod
    def change_password(db: Session, username: str, password: str, new_password: str):
        user = UsersRepository.get_by_username(db, username)

        if not user or not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        hashed_password = hash_password(new_password)
        updated_user = UsersRepository.update_password(db, user, hashed_password)

        return updated_user
