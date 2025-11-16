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
        
        if sort_by not in TasksService.ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )
        
        filters = []
        
        if my_tasks:
            related_to_user = current_user.username

        if related_to_user:
            filters.append(TasksRepository.get_by_username(db, related_to_user))

        if search:
            filters.append(TasksRepository.search(search))

        query = TasksRepository.apply_filters(query, sort_by, order)
        query = TasksRepository.apply_sorting(query, sort_by, order)
        total_tasks = TasksRepository.count(query)
        tasks = TasksRepository.paginate(query, skip, limit)

        return TasksListResponse(
            total=total_tasks,
            skip=skip,
            limit=limit,
            tasks=[TasksListResponse.model_validate(task) for task in tasks]
        )

    @staticmethod
    def take_task(
            db: Session,
            status: str,
            current_user,
            task_id: int | None,
            title: str
    ) -> StatusTasksResponse:
        
        if task_id:
            db_task = TasksRepository.get_by_id(task_id)
        else:
            db_task = TasksRepository.get_by_title(title)

        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        if db_task.user_id and db_task.user_id != current_user.id:
            raise HTTPException(status_code=400, detail=f"Task {db_task.name} is already assigned.")
        
        try:
            taken_task = TasksRepository.update(db, 
                                                   db_task, 
                                                   current_user.id,
                                                   db_task.title, 
                                                   db_task.description, 
                                                   status,
                                                   db_task.due_date)
            return StatusTasksResponse(
                status="changed",
                tasks=TaskRead.model_validate(taken_task)
            )
        except Exception as e:
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
            db_task = TasksRepository.get_by_id(task_id)
        else:
            db_task = TasksRepository.get_by_title(title)

        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        assigned_user = UsersRepository.get_by_username(db, task.user_name)
        if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            updated_task = TasksRepository.update(db, 
                                                       db_task, 
                                                       assigned_user.id,
                                                       task.title, 
                                                       task.description, 
                                                       task.status,
                                                       task.due_date)
            
            return StatusTasksResponse(
                status="changed",
                tasks=TaskRead.model_validate(updated_task)
            )
        except Exception as e:
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to update task: {str(e)}")

    @staticmethod
    def add(
            task: TaskCreate,
            db: Session,
    ) -> StatusTasksResponse:
        
        if TasksRepository.get_by_title(db, task.title):
            raise HTTPException(status_code=404, detail='Task already exists')
        
        user_id = None
        user_name = task.user_name
        
        if task.user_name:
            assigned_user = UsersRepository.get_by_username(db, user_name)

            if not assigned_user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id = assigned_user.id

        try:
            created_task = TasksRepository.add(db, 
                                               user_id,
                                               task.title,
                                               task.description, 
                                               task.status,
                                               task.due_date)
            
            return StatusTasksResponse(
                status="created",
                tasks=TaskRead.model_validate(created_task)
            )
        except Exception as e:
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to create task: {str(e)}")

    @staticmethod
    def delete_task(
            db: Session,
            task_id: int | None,
            title: str
    ) -> StatusTasksResponse:
        
        if task_id:
            db_task = TasksRepository.get_by_id(db, task_id)
        else:
            db_task = TasksRepository.get_by_title(db, title)

        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        try:
            deleted_task = TasksRepository.delete(db, db_task)
            
            return StatusTasksResponse(
                status="deleted_task",
                tasks=TaskRead.model_validate(deleted_task)
            )
        
        except Exception as e:
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete task: {str(e)}")

    @staticmethod
    def delete_done_tasks(
            db: Session,
    ) -> StatusTasksResponse:
        
        query = TasksRepository.get_all_done(db)

        try:
            deleted_tasks = TasksRepository.delete_group(db, query)
            return StatusTasksResponse(
                status="deleted",
                tasks=TaskRead.model_validate(deleted_tasks)
            )
        
        except Exception as e:
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete task: {str(e)}")

    @staticmethod
    def delete_expired_tasks(
            db: Session,
    ) -> StatusTasksResponse:
        
        query = TasksRepository.get_all_expired(db)

        try:
            deleted_tasks = TasksRepository.delete_group(db, query)
            return StatusTasksResponse(
                status="deleted",
                tasks=TaskRead.model_validate(deleted_tasks)
            )
        
        except Exception as e:
            TasksRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete task: {str(e)}")
        