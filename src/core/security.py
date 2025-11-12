from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from src.core.config import settings
import jwt

argon2_context = CryptContext(schemes=["argon2"], deprecated="auto")

class JWTValidationError(Exception):
    pass

def hash_password(password: str) -> str:
    return argon2_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon2_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            return None
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return payload if exp_datetime >= datetime.now(timezone.utc) else None
    except jwt.PyJWTError:
        raise JWTValidationError(status_code=401, detail="Invalid or expired token")
    
