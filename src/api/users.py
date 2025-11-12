from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.models import User
from src.schemas import UserCreate, UserRead, UserRole

router = APIRouter(tags=['Users'])

@router.get("/users/me", response_model=UserRead)
async def get_my_info(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user

@router.get("/users/get", response_model=List[UserRead])
async def get_users(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager'))
                    ) -> List[UserRead]:
    return db.query(User).all()

@router.get("/users/get/role/{user_role}", response_model=List[UserRead])
async def get_users_by_role(user_role: UserRole, 
                            db: Session = Depends(get_db),
                            _: User = Depends(require_roles('admin', 'manager'))
                            ) -> List[UserRead]:
    users = db.query(User).filter(User.role == user_role).all()
    return users

@router.post("/users/add", response_model=UserRead)
async def create_user(user: UserCreate, 
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> UserRead:
    user = db.query(User).filter(User.name == user.username).first()
    if user:
        raise HTTPException(status_code=404, detail="User already exists")

    db_user = User(username=user.username, 
                   password=user.password,
                   role=user.role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    except Exception as e:
        db.rollback() 
        raise e

    return db_user

@router.put("/users/update/{user_id}", response_model=UserRead)
async def update_user(user_id: int, 
                      user: UserCreate,
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> UserRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = user.username
    user.password = user.password
    user.role = user.role
    
    db.commit()
    db.refresh(user)

    return user

@router.delete("/users/delete/{user_id}", response_model=List[UserRead])
async def delete_user(user_id: int, 
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> List[UserRead]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return db.query(User).all()
