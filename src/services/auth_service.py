from src.core.logger import logger
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
        logger.info('Logging user %s', username)
        user = UsersRepository.get_by_username(db, username)

        if not user or not verify_password(password, user.password):
            logger.warning("Invalid login attempt: username=%s " \
            "Invalid credentials", username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({
            "sub": user.username,
            "role": user.role
        })

        logger.info('Login successful for %s', username)

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    @staticmethod
    def change_password(db: Session, username: str, password: str, new_password: str):
        logger.info('Changing %s user password', username)
        user = UsersRepository.get_by_username(db, username)

        if not user or not verify_password(password, user.password):
            logger.warning("Invalid password change attempt: username=%s " \
            "Invalid credentials", username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        try:
            hashed_password = hash_password(new_password)
            updated_user = UsersRepository.update_password(db, user, hashed_password)
        except Exception as e:
            UsersRepository.rollback(db)
            logger.warning("Invalid password change attempt: username=%s ", username)
            raise HTTPException(500, f"Failed to change password: {str(e)}")

        logger.info('Password change successful for %s', username)
        return updated_user
