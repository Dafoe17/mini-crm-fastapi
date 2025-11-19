from src.core.logger import logger
from fastapi import APIRouter, Query, Depends
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.services.users_service import UsersService
from src.enums import UserRole, SortOrder
from src.models import User
from src.schemas.user import UserCreate, UserRead, UsersListResponse, StatusUsersResponse


router = APIRouter(tags=['Users'])

@router.get("/users/me", response_model=UserRead, operation_id="my-info")
async def get_my_info(current_user: User = Depends(get_current_user)) -> UserRead:
    logger.info('User %s requested info about his account', current_user.username)
    return current_user

@router.get("/users/get-all-users", response_model=UsersListResponse, operation_id="get-all-users")
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "manager")),
    skip: int = Query(None),
    limit: int = Query(None),
    role: UserRole | None = Query(None),
    search: str | None = Query(None),
    sort_by: str = Query("id"),
    order: SortOrder = Query("asc"),
    ):
    logger.info('User %s requested info about all users with attributes: ' \
    'skip=%s, limit=%s, role=%s, search=%s, sort_by=%s, order=%s', current_user.username, skip, limit, role, search, sort_by, order)
    return UsersService.get_all(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        search=search,
        sort_by=sort_by,
        order=order,
    )

@router.get("/users/get-user-by-id/{user_id}", response_model=UsersListResponse, operation_id="get-user-by-id")
async def get_user_by_id(user_id: int,
                        db: Session = Depends(get_db), 
                        current_user: User = Depends(require_roles('admin', 'manager')),
                    ):
    logger.info('User %s requested info about user by id - %s', current_user.username, user_id)
    return UsersService.get_user_by_id(
        user_id=user_id,
        db=db,
    )

@router.get("/users/get-user-by-username/{username}", response_model=UsersListResponse, operation_id="get-user-by-username")
async def get_user_by_username(
    username: str,
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles('admin', 'manager')),
    ):
    logger.info('User %s requested info about user %s', current_user.username, username)
    return UsersService.get_user_by_username(
        username=username,
        db=db,
    )

@router.post("/users/add", response_model=StatusUsersResponse, operation_id="add-user")
async def add_user(
    user: UserCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin'))
    ):
    logger.info('User %s requested creating user %s', current_user.username, user.username)
    return UsersService.add_user(
        user=user,
        db=db,
    )

@router.put("/users/update/{user_id}", response_model=StatusUsersResponse, operation_id="update-user")
async def update_user(
    user: UserCreate,
    username: str = Query(description="Search by username"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin')),
    ):
    logger.info('User %s requested updating user %s', current_user.username, user.username)
    return UsersService.update_user(
        user=user,
        username=username,
        db=db,
    )

@router.delete("/users/delete/{user_id}", response_model=StatusUsersResponse, operation_id="delete-user")
async def delete_user(
    username: str = Query(description="Search by user name"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin'))
    ):
    logger.info('User %s requested deleting user %s', current_user.username, username)
    return UsersService.delete_user(
        username=username,
        db=db,
    )
