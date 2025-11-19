from src.core.logger import logger
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
        
        logger.debug('Trying to get all users')
        if sort_by not in UsersService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        filters = []

        if role:
            logger.debug('Add role filter (%s)', role)
            filters.append(UsersRepository.filter_by_role(role))

        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(UsersRepository.search(search))

        sort_by = "role_level" if sort_by == "role" else sort_by

        logger.debug('Applying filters')
        query = UsersRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = UsersRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total = UsersRepository.count(query)
        logger.debug('Paginating')
        users = UsersRepository.paginate(query, skip, limit)

        logger.debug('Forming UsersListResponse')
        response = UsersListResponse(
            total=total,
            skip=skip,
            limit=limit,
            users=[UserRead.model_validate(user) for user in users]
        )
        logger.info('Success')
        return response
    
    @staticmethod
    def get_user_by_id(
        user_id: int,
        db: Session,
    ) -> UsersListResponse:

        logger.debug('Trying to all user by id')
        user = UsersRepository.get_by_id(db, user_id)

        if not user:
            logger.warning('User (%s) not found', user_id)
            raise HTTPException(status_code=400, detail=f"User with id {user_id} not found")

        logger.debug('Forming UsersListResponse')
        response = UsersListResponse(
            total=1,
            skip=None,
            limit=None,
            users=UserRead.model_validate(user)
        )
        logger.info('Success')
        return response
    
    @staticmethod
    def get_user_by_username(
        username: str,
        db: Session,
    ) -> UsersListResponse:

        logger.debug('Trying to user by username')
        user = UsersRepository.get_by_username(db, username)

        if not user:
            logger.warning('User (%s) not found', username)
            raise HTTPException(status_code=400, detail=f"User {username} not found")

        logger.debug('Forming UsersListResponse')
        response = UsersListResponse(
            total=1,
            skip=None,
            limit=None,
            users=UserRead.model_validate(user)
        )
        logger.info('Success')
        return response
    
    @staticmethod
    def add_user(
        user: UserCreate,
        db: Session,
    ) -> StatusUsersResponse:
        
        db_user = UsersRepository.get_by_username(db, user.username)
        
        if db_user:
            logger.warning('User (%s) already exists', db_user.username)
            raise HTTPException(status_code=400, detail="User already exists")

        try:
            logger.debug('Trying to add user')
            new_user = UsersRepository.add(
                db=db,
                username=user.username, 
                password=user.password,
                role=user.role
            )
            logger.debug('Forming StatusUsersResponse')
            responce = StatusUsersResponse(
                status="created",
                users=UserRead.model_validate(new_user)
            )
            logger.info('Success')
            return responce
        except Exception as e:
            logger.error('Failed to create user: %s', str(e))
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(
        user: UserCreate,
        username: str,
        db: Session,
    ) -> StatusUsersResponse:

        db_user = UsersRepository.get_by_username(db, username)
        
        if db_user:
            logger.warning('User (%s) already exists', db_user.username)
            raise HTTPException(status_code=404, detail="User already exists")

        try:
            logger.debug('Trying to update user')
            changed_user = UsersRepository.update(db, db_user, user.username, user.password, user.role)
            logger.debug('Forming StatusUsersResponse')
            response = StatusUsersResponse(
                status="changed",
                users=UserRead.model_validate(changed_user)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to update user: %s', str(e))
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to change user: {str(e)}")
        
    @staticmethod
    def delete_user(
        username: str,
        db: Session,
    ) -> StatusUsersResponse:

        db_user = UsersRepository.get_by_username(db, username)
        
        if not db_user:
            logger.warning('User (%s) not exists', username)
            raise HTTPException(status_code=404, detail="User not found")

        try:
            logger.debug('Trying to delete user')
            deleted_user = UsersRepository.delete(db, db_user)
            logger.debug('Forming StatusUsersResponse')
            response = StatusUsersResponse(
                status="deleted",
                users=UserRead.model_validate(deleted_user)
            )
            logger.debug('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete user: %s', str(e))
            UsersRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete user: {str(e)}")
        