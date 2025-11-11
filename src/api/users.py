from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List

from src.database import Session, get_db
from src.models import Base, User
from src.schemas import UserCreate, UserRead

router = APIRouter(tags=['Users'])


@router.get("/users/get", response_model=List[UserRead])
async def get_users(db: Session = Depends(get_db)) -> List[UserRead]:
    return db.query(User).all()

@router.post("/users/add", response_model=UserRead)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    db_user = User(username=user.username, 
                   password=user.password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    except Exception as e:
        db.rollback() 
        raise e
    
    return db_user


@router.delete("/users/delete/{user_id}", response_model=List[UserRead])
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> List[UserRead]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return db.query(User).all()