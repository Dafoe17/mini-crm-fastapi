from src.database import Session_local
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from src.core.security import verify_access_token, JWTValidationError
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Get db Session
def get_db():
    db: Session = Session_local()
    try:
        yield db
    finally:
        db.close()

# Get user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)) -> User:
    try:
        payload = verify_access_token(token)

    except JWTValidationError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = db.query(User).filter(User.username == payload["sub"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_role(role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {role}"
            )
        return current_user
    return role_checker


def require_roles(*allowed_roles: str):
    def roles_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return roles_checker
