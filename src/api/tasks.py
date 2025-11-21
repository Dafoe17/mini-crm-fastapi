from src.core.logger import logger
from fastapi import APIRouter, HTTPException, Depends, Query
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.services.tasks_service import TasksService
from datetime import datetime, timezone
from src.enums import SortOrder, TaskStatus
from src.models import User, Task
from src.schemas.task import TaskRead, TaskCreate, TasksListResponse, StatusTasksResponse

router = APIRouter(tags=['Tasks'])

@router.get("/tasks/get", response_model=TasksListResponse, operation_id="get-tasks")
async def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(None, description="Number of tasks to skip"),
    limit: int = Query(None, description="Number of tasks to return"),
    search: str | None = Query(None, description="Search by title, description or status"),
    related_to_user: str | None = Query(None, description="Filter tasks related to user"),
    my_tasks: bool = Query(False, description="Filter tasks related to your user"),
    sort_by: str = Query("id", description="Sort by field: id, title, status"),
    order: SortOrder = Query("asc", description="Sort order: asc or desc")
    ):
    logger.info('User %s requested info about all tasks with attributes: ' \
                'skip=%s, limit=%s, search=%s, related_to_user=%s, my_tasks=%s ' \
                'sort_by=%s,order=%s', 
                current_user.username, skip, limit, search, related_to_user, my_tasks, sort_by, order)
    return TasksService.get_all(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        related_to_user=related_to_user,
        my_tasks=my_tasks,
        sort_by=sort_by,
        order=order
    )

@router.patch("/tasks/take", response_model=StatusTasksResponse, operation_id="take-task")
async def take_task(
    db: Session = Depends(get_db),
    status: TaskStatus = Query("doing", description="Set new status: todo, doing or done"),
    current_user: User = Depends(get_current_user),
    task_id: int | None = Query(None, description="Search task by id"),
    title: str = Query("", description="Search task by title"),
    ):
    logger.info('User %s requested take task (%s, %s) with status %s',
                current_user.username, task_id, title, status)
    return TasksService.take_task(
        db=db,
        status=status,
        current_user=current_user,
        task_id=task_id,
        title=title
    )

@router.put("/tasks/update", response_model=StatusTasksResponse, operation_id="update-task")
async def update_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    task_id: int | None = Query(None, description="Search task by id"),
    title: str = Query("", description="Search task by title"),
    ):
    logger.info('User %s requested update task (%s, %s)',
                current_user.username, task_id, title)
    return TasksService.update_task(
        task=task,
        db=db,
        task_id=task_id,
        title=title
    )

@router.post("/tasks/add", response_model=StatusTasksResponse, operation_id="add-task")
async def add_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager'))
    ):
    logger.info('User %s requested add task (%s)',
                current_user.username, task.title)
    return TasksService.add(
        task=task,
        db=db
    )

@router.delete("/tasks/delete", response_model=StatusTasksResponse, operation_id="delete-task")
async def delete_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    task_id: int | None = Query(None, description="Search task by id"),
    title: str = Query("", description="Search task by title")
    ):
    logger.info('User %s requested add task (%s, %s)',
                current_user.username, task_id, title)
    if task_id:
        db_task = db.query(Task).filter(Task.id == task_id).first()
    else:
        db_task = db.query(Task).filter((Task.title.ilike(f"%{title}%"))).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        db.delete(db_task)
        db.commit()
        response = StatusTasksResponse(
            status="deleted",
        )
    except Exception as e:
        db.rollback()
        response = StatusTasksResponse(
            status="error",
            details=f"Failed to delete client: {str(e)}"
        )

    response.tasks = TaskRead.model_validate(db_task)

    return response

@router.delete("/tasks/delete-done-task", response_model=StatusTasksResponse, operation_id="delete-done-tasks")
async def delete_done_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    ):
    logger.info('User %s requested delete done tasks',
                current_user.username)
    return TasksService.delete_done_tasks(
        db=db
    )

@router.delete("/tasks/delete-expired-task", response_model=StatusTasksResponse, operation_id="delete-expired-tasks")
async def delete_expired_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    ):
    logger.info('User %s requested expired tasks',
                current_user.username)
    return TasksService.delete_expired_tasks(
        db=db
    )
