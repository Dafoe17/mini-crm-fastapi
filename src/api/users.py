from fastapi import APIRouter, HTTPException, Query, Depends
from src.api.dependencies import Session, get_db, get_current_user, require_roles
from typing import Optional

from src.enums import SortOrder
from src.models import User
from src.schemas.user import UserCreate, UserRead, UsersListResponse, StatusUsersResponse, UserRole


router = APIRouter(tags=['Users'])

@router.get("/users/me", response_model=UserRead, operation_id="my-info")
async def get_my_info(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user

@router.get("/users/get-all-users", response_model=UsersListResponse, operation_id="get-all-users")
async def get_all_users(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    skip: int = Query(None, description="Number of users to skip"),
                    limit: int = Query(None, description="Number of users to return"),
                    role: UserRole | None = Query(None, description="Filter by role"),
                    search: str | None = Query(None, description="Search by username"),
                    sort_by: str = Query("id", description="Sort by field: id, username, role"),
                    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                    ) -> UsersListResponse:
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))
    
    sort_by = "role_level" if sort_by == "role" else sort_by

    if hasattr(User, sort_by):
        sort_attr = getattr(User, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_users = query.count()
    users = query.offset(skip).limit(limit).all()

    return UsersListResponse(
        total=total_users,
        skip=skip,
        limit=limit,
        users=[UserRead.model_validate(user) for user in users]
    )

@router.get("/users/get-user-by-id", response_model=UsersListResponse, operation_id="get-user-by-id")
async def get_user_by_id(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    user_id = int,
                    ) -> UsersListResponse:

    db_user = db.query(User).filter(User.id == user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    return UsersListResponse(
        total=1,
        skip=None,
        limit=None,
        users=UserRead.model_validate(db_user)
    )

@router.post("/users/add", response_model=StatusUsersResponse, operation_id="add-user")
async def create_user(user: UserCreate, 
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> StatusUsersResponse:
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=404, detail="User already exists")

    db_user = User(username=user.username, 
                   password=user.password,
                   role=user.role)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        response = StatusUsersResponse(
            status="create",
        )
    
    except Exception as e:
        db.rollback() 
        response = StatusUsersResponse(
            status="error",
            details=f"Failed to create user: {str(e)}"
        )

    response.users = UserRead.model_validate(db_user)

    return response

@router.put("/users/update/{user_id}", response_model=StatusUsersResponse, operation_id="update-user")
async def update_user(user: UserCreate,
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin')),
                      name: str = Query(description="Search by user name")
                      ) -> StatusUsersResponse:
    
    db_user = db.query(User).filter(User.username == name).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.username = user.username
    db_user.password = user.password
    db_user.role = user.role

    try:
        db.commit()
        db.refresh(db_user)
        response = StatusUsersResponse(
            status="changed",
        )
    
    except Exception as e:
        db.rollback() 
        response = StatusUsersResponse(
            status="error",
            details=f"Failed to change user: {str(e)}"
        )

    response.users = UserRead.model_validate(db_user)

    return response

@router.delete("/users/delete/{user_id}", response_model=StatusUsersResponse, operation_id="delete-user")
async def delete_user(name: str = Query(description="Search by user name"), 
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin'))
                      ) -> StatusUsersResponse:
    if not name:
        raise HTTPException(status_code=400, detail="No search criteria provided")
    
    db_user = db.query(User).filter(User.username == name).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        db.delete(db_user)
        db.commit()
        response = StatusUsersResponse(
            status="deleted",
        )
    
    except Exception as e:
        db.rollback() 
        response = StatusUsersResponse(
            status="error",
            details=f"Failed to delete user: {str(e)}"
        )

    response.users = UserRead.model_validate(db_user)

    return response
