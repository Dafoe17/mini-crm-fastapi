from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.user import UsersListResponse, StatusUsersResponse, UserRead, UserCreate
from src.repositories.users_repository import UsersRepository


class UsersService:

    ALLOWED_SORT_FIELDS = {"id", "username", "role"}

    @staticmethod
    def get_all(
        db: Session,
        skip: int | None,
        limit: int | None,
        role,
        search: str | None,
        sort_by: str,
        order: str
    ) -> UsersListResponse:
        
        if sort_by not in UsersService.ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        filters = []

        if role:
            filters.append(UsersRepository.filter_by_role(query, role))

        if search:
            filters.append(UsersRepository.search(query, search))

        sort_by = "role_level" if sort_by == "role" else sort_by

        query = UsersRepository.apply_filters(db, filters)
        query = UsersRepository.apply_sorting(query, sort_by, order)
        total = UsersRepository.count(query)
        users = UsersRepository.paginate(query, skip, limit)

        return UsersListResponse(
            total=total,
            skip=skip,
            limit=limit,
            users=[UserRead.model_validate(user) for user in users]
        )
    
    @staticmethod
    def get_user_by_id(
        user_id: int,
        db: Session,
    ) -> UsersListResponse:

        user = UsersRepository.get_by_id(db, user_id)

        if not user:
            raise HTTPException(status_code=400, detail=f"User with id {user_id} not found")

        return UsersListResponse(
            total=1,
            skip=None,
            limit=None,
            users=UserRead.model_validate(user)
        )
    
    @staticmethod
    def get_user_by_username(
        username: str,
        db: Session,
    ) -> UsersListResponse:

        user = UsersRepository.get_by_username(db, username)

        if not user:
            raise HTTPException(status_code=400, detail=f"User {username} not found")

        return UsersListResponse(
            total=1,
            skip=None,
            limit=None,
            users=UserRead.model_validate(user)
        )
    
    @staticmethod
    def add_user(
        user: UserCreate,
        db: Session,
    ) -> StatusUsersResponse:

        db_user = UsersRepository.get_by_username(db, user.username)
        
        if db_user:
            raise HTTPException(status_code=400, detail="User already exists")

        try:
            new_user = UsersRepository.add(
                db=db,
                username=user.username, 
                password=user.password,
                role=user.role
            )
            return StatusUsersResponse(
                status="created",
                users=UserRead.model_validate(new_user)
            )
        except Exception as e:
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(
        user: UserCreate,
        username: str,
        db: Session,
    ) -> StatusUsersResponse:

        db_user = UsersRepository.get_by_username(db, username)
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            changed_user = UsersRepository.update(db, db_user, user.username, user.password, user.role)
            return StatusUsersResponse(
                status="changed",
                users=UserRead.model_validate(changed_user)
            )
        except Exception as e:
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to change user: {str(e)}")
        
    @staticmethod
    def delete_user(
        username: str,
        db: Session,
    ) -> StatusUsersResponse:

        db_user = UsersRepository.get_by_username(db, username)
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            deleted_user = UsersRepository.delete(db, db_user)
            return StatusUsersResponse(
                status="deleted",
                users=UserRead.model_validate(deleted_user)
            )
        except Exception as e:
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete user: {str(e)}")
        