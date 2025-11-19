from src.core.logger import logger
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from src.schemas.task import TasksListResponse, StatusTasksResponse, TaskRead, TaskCreate
from src.repositories.tasks_repository import TasksRepository
from src.repositories.users_repository import UsersRepository


class TasksService:

    ALLOWED_SORT_FIELDS = {"id", "tittle", "status"}

    @staticmethod
    def get_all(
        db: Session,
        current_user,
        skip: int | None,
        limit: int | None,
        search: str | None,
        related_to_user: str | None,
        my_tasks: bool,
        sort_by: str,
        order: str
    ) -> StatusTasksResponse:
        
        logger.debug('Trying to get all tasks')
        if sort_by not in TasksService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )
        
        filters = []
        
        if my_tasks:
            logger.debug('Add my_tasks filter (%s)', my_tasks)
            related_to_user = current_user.username

        if related_to_user:
            logger.debug('Add related_to_user filter (%s)', related_to_user)
            filters.append(TasksRepository.get_by_username(db, related_to_user))

        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(TasksRepository.search(search))

        logger.debug('Applying filters')
        query = TasksRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = TasksRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total_tasks = TasksRepository.count(query)
        logger.debug('Paginating')
        tasks = TasksRepository.paginate(query, skip, limit)

        logger.debug('Forming TasksListResponse')
        response = TasksListResponse(
            total=total_tasks,
            skip=skip,
            limit=limit,
            tasks=[TaskRead.model_validate(task) for task in tasks]
        )
        logger.info('Success')
        return response

    @staticmethod
    def take_task(
            db: Session,
            status: str,
            current_user,
            task_id: int | None,
            title: str
    ) -> StatusTasksResponse:
        
        if task_id:
            logger.debug('Searching by id')
            db_task = TasksRepository.get_by_id(db, task_id)
        else:
            logger.debug('Searching by title')
            db_task = TasksRepository.get_by_title(db, title)

        if not db_task:
            logger.warning('Task not found')
            raise HTTPException(status_code=404, detail="Task not found")
        
        if db_task.user_id and db_task.user_id != current_user.id:
            logger.warning('Task is already assigned')
            raise HTTPException(status_code=400, detail=f"Task {db_task.name} is already assigned.")
        
        try:
            logger.debug('Trying take task')
            taken_task = TasksRepository.update(db, 
                                                   db_task, 
                                                   current_user.id,
                                                   db_task.title, 
                                                   db_task.description, 
                                                   status,
                                                   db_task.due_date)
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="changed",
                tasks=TaskRead.model_validate(taken_task)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to take task')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to take task: {str(e)}")

    @staticmethod
    def update_task(
            task: TaskCreate,
            db: Session,
            task_id: int | None,
            title: str
    ) -> StatusTasksResponse:
        
        if task_id:
            logger.debug('Searching by id')
            db_task = TasksRepository.get_by_id(db, task_id)
        else:
            logger.debug('Searching by title')
            db_task = TasksRepository.get_by_title(db, title)

        if not db_task:
            logger.warning('Task not found')
            raise HTTPException(status_code=404, detail="Task not found")
        
        assigned_user = UsersRepository.get_by_username(db, task.user_name)
        if not assigned_user:
            logger.warning('User not found')
            raise HTTPException(status_code=404, detail="User not found")

        try:
            logger.debug('Trying update task')
            updated_task = TasksRepository.update(db, 
                                                       db_task, 
                                                       assigned_user.id,
                                                       task.title, 
                                                       task.description, 
                                                       task.status,
                                                       task.due_date)
            
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="changed",
                tasks=TaskRead.model_validate(updated_task)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to update task')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to update task: {str(e)}")

    @staticmethod
    def add(
            task: TaskCreate,
            db: Session,
    ) -> StatusTasksResponse:
        
        if TasksRepository.get_by_title(db, task.title):
            logger.warning('Task already exists')
            raise HTTPException(status_code=404, detail='Task already exists')
        
        user_id = None
        user_name = task.user_name
        
        if task.user_name:
            logger.debug('Searching by user_name')
            assigned_user = UsersRepository.get_by_username(db, user_name)

            if not assigned_user:
                logger.warning('User not found')
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id = assigned_user.id

        try:
            logger.debug('Trying add task')
            created_task = TasksRepository.add(db, 
                                               user_id,
                                               task.title,
                                               task.description, 
                                               task.status,
                                               task.due_date)
            
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="created",
                tasks=TaskRead.model_validate(created_task)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to create task')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to create task: {str(e)}")

    @staticmethod
    def delete_task(
            db: Session,
            task_id: int | None,
            title: str
    ) -> StatusTasksResponse:
        
        if task_id:
            logger.debug('Searching by id')
            db_task = TasksRepository.get_by_id(db, task_id)
        else:
            logger.debug('Searching by title')
            db_task = TasksRepository.get_by_title(db, title)

        if not db_task:
            logger.warning('Task not found')
            raise HTTPException(status_code=404, detail="Task not found")

        try:
            logger.debug('Trying delete task')
            deleted_task = TasksRepository.delete(db, db_task)
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="deleted",
                tasks=TaskRead.model_validate(deleted_task)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete task')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete task: {str(e)}")

    @staticmethod
    def delete_done_tasks(
            db: Session,
    ) -> StatusTasksResponse:
        
        logger.debug('Getting all done tasks')
        query = TasksRepository.get_all_done(db)

        try:
            logger.debug('Trying delete all done tasks')
            deleted_tasks = TasksRepository.delete_group(db, query)
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="deleted",
                tasks=[TaskRead.model_validate(deleted_task) for deleted_task in deleted_tasks]
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete tasks')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete tasks: {str(e)}")

    @staticmethod
    def delete_expired_tasks(
            db: Session,
    ) -> StatusTasksResponse:
        
        logger.debug('Getting all expired tasks')
        query = TasksRepository.get_all_expired(db)

        try:
            logger.debug('Trying delete all expired tasks')
            deleted_tasks = TasksRepository.delete_group(db, query)
            logger.debug('Forming StatusTasksResponse')
            response = StatusTasksResponse(
                status="deleted",
                tasks=[TaskRead.model_validate(deleted_task) for deleted_task in deleted_tasks]
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete tasks')
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete tasks: {str(e)}")
        