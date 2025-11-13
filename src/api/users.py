from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.models import User
from src.schemas.user import UserCreate, UserRead, UsersListResponse, StatusUsersResponse, UserRole

router = APIRouter(tags=['Users'])

@router.get("/users/me", response_model=UserRead, operation_id="my-info")
async def get_my_info(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user

@router.get("/users/get", response_model=UsersListResponse, operation_id="get-all-users")
async def get_users(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    skip: int = Query(None, description="Number of users to skip"),
                    limit: int = Query(None, description="Number of users to return")
                    ) -> Dict:
    total_users = db.query(User).count()
    users = db.query(User).offset(skip).limit(limit).all()
    return UsersListResponse(
        total=total_users,
        skip=skip,
        limit=limit,
        users=[UserRead.model_validate(user) for user in users]
    )

@router.get("/users/get/by_role/{user_role}", response_model=UsersListResponse, operation_id="get-users-by-role")
async def get_users_by_role(user_role: UserRole, 
                            db: Session = Depends(get_db),
                            _: User = Depends(require_roles('admin', 'manager')),
                            skip: int = Query(None, description="Number of users to skip"),
                            limit: int = Query(None, description="Number of users to return")
                            ) -> List[UserRead]:
    total_users = db.query(User).filter(User.role == user_role).count()
    users = db.query(User).filter(User.role == user_role).offset(skip).limit(limit).all()
    return UsersListResponse(
        total=total_users,
        skip=skip,
        limit=limit,
        users=[UserRead.model_validate(user) for user in users]
    )

@router.post("/users/add", response_model=StatusUsersResponse, operation_id="add-user")
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

    return StatusUsersResponse(
        status='created',
        users=db_user
    )

@router.put("/users/update/{user_id}", response_model=StatusUsersResponse, operation_id="update-user")
async def update_user(user_id: int, 
                      user: UserCreate,
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> Dict:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.username = user.username
    db_user.password = user.password
    db_user.role = user.role
    
    db.commit()
    db.refresh(db_user)

    return StatusUsersResponse(
            status="changed",
            users=db_user
    )

@router.delete("/users/delete/{user_id}", response_model=StatusUsersResponse, operation_id="delete-user")
async def delete_user(user_id: int, 
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> List[UserRead]:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return StatusUsersResponse(
            status="deleted",
            users=db_user
        )
