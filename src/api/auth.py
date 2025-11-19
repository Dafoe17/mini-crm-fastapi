from src.core.logger import logger
from fastapi import APIRouter, Depends, Form
from src.api.dependencies import get_db, Session

from src.services.auth_service import AuthService

router = APIRouter(tags=["Auth"])

@router.post("/auth/login")
async def login(
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db)
):
    logger.info('User %s trying to login', username)
    return AuthService.login(db, username, password)


@router.patch("/auth/change-password")
async def change_password(
    username: str,
    password: str,
    new_password: str,
    db: Session = Depends(get_db)
): 
    logger.info('User %s requested password change', username)
    return AuthService.change_password(db, username, password, new_password)