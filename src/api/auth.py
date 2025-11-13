from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from src.api.dependencies import get_db
from src.models import User
from src.core.security import verify_password, create_access_token 

router = APIRouter(tags=["Auth"])

@router.post("/auth/login", operation_id="login")
async def login(username: str = Form(),
                password: str = Form(),
                db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.patch("/auth/change-password", operation_id="change-password")
async def change_password(username: str,
                          password: str,
                          new_password: str,
                          db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.username = username
    user.password = new_password
    
    db.commit()
    db.refresh(user)

    return user
