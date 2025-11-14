from fastapi import APIRouter, HTTPException, Depends, Query
from src.api.dependencies import Session, get_db, get_current_user, require_roles
from datetime import datetime, timezone
from src.enums import SortOrder, TaskStatus
from src.models import User, Task
from src.schemas.task import TaskRead, TaskCreate, TasksListResponse, StatusTasksResponse

router = APIRouter(tags=['Tasks'])

@router.get("/tasks/get", response_model=TasksListResponse, operation_id="get-tasks")
async def get_tasks(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user),
                    skip: int = Query(None, description="Number of tasks to skip"),
                    limit: int = Query(None, description="Number of tasks to return"),
                    search: str | None = Query(None, description="Search by title, description or status"),
                    related_to_user: str | None = Query(None, description="Filter tasks related to user"),
                    my_tasks: bool = Query(False, description="Filter tasks related to your user"),
                    sort_by: str = Query("id", description="Sort by field: id, title, status"),
                    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                    ) -> TasksListResponse:
    
    query = db.query(Task)

    if related_to_user:
        user_ids = db.query(User.id).filter(User.username.ilike(f"%{related_to_user}%")).subquery()
        query = query.filter(Task.user_id.in_(user_ids))
    
    if search:
        query = query.filter(
        (Task.title.ilike(f"%{search}%")) |
        (Task.description.ilike(f"%{search}%")) |
        (Task.status.ilike(f"%{search}%")))

    if hasattr(Task, sort_by):
        sort_attr = getattr(Task, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_tasks = query.count()
    tasks = query.offset(skip).limit(limit).all()

    return TasksListResponse(
        total=total_tasks,
        skip=skip,
        limit=limit,
        clients=[TaskRead.model_validate(Task) for task in tasks]
    )

@router.patch("/tasks/take", response_model=TasksListResponse, operation_id="take-task")
async def take_task(db: Session = Depends(get_db),
                    status: TaskStatus = Query("doing", description="Set new status: todo, doing or done"),
                    current_user: User = Depends(get_current_user),
                    task_id: int | None = Query(None, description="Search task by id"),
                    title: str = Query("", description="Search task by title"),
                    ) -> TasksListResponse:

    if task_id:
        db_task = db.query(Task).filter(Task.id == task_id).first()
    else:
        db_task = db.query(Task).filter((Task.title.ilike(f"%{title}%"))).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if db_task.user_id and db_task.user_id != current_user.id:
        raise HTTPException(status_code=400, detail=f"Task {db_task.name} is already assigned.")

    db_task.user_id = current_user.id
    db_task.status = status

    try:
        db.commit()
        db.refresh(db_task)
        response = StatusTasksResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusTasksResponse(
            status="error",
            details=f"Failed to take task: {str(e)}"
        )

    response.tasks = TaskRead.model_validate(db_task)\
    
    return response

@router.put("/tasks/update", response_model=TasksListResponse, operation_id="update-task")
async def update_task(task: TaskCreate,
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin', 'manager')),
                      task_id: int | None = Query(None, description="Search task by id"),
                      title: str = Query("", description="Search task by title"),
                      ) -> TasksListResponse:
    
    if task_id:
        db_task = db.query(Task).filter(Task.id == task_id).first()
    else:
        db_task = db.query(Task).filter((Task.title.ilike(f"%{title}%"))).first()

    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    assigned_user = db.query(User).filter(User.username == task.user_name).first()

    if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")

    db_task.user_id = assigned_user.id
    db_task.title = task.title
    db_task.description = task.description
    db_task.due_date = task.due_date
    db_task.status = task.status


    try:
        db.commit()
        db.refresh(db_task)
        response = StatusTasksResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusTasksResponse(
            status="error",
            details=f"Failed to change task: {str(e)}"
        )

    response.tasks = TaskRead.model_validate(db_task)\
    
    return response

@router.post("/tasks/add", response_model=StatusTasksResponse, operation_id="add-task")
async def add_task(task: TaskCreate, 
                    db: Session = Depends(get_db),
                    _: User = Depends(require_roles('admin', 'manager'))
                    ) -> StatusTasksResponse:
    
    query = db.query(Task).filter(task.title == task.title).first()
    if query:
        raise HTTPException(status_code=404, detail='Deal already exists')
    
    user_id = None
    username = Task.user_name

    if username:
        assigned_user = db.query(User).filter(User.username == username).first()

        if not assigned_user:
                raise HTTPException(status_code=404, detail="User not found")

        user_id = assigned_user.id
    

    db_task = Task(user_id=user_id,
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    due_date=task.due_date)
    
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except:
        db.rollback() 
    return db_task

@router.delete("/tasks/delete-taks", response_model=StatusTasksResponse, operation_id="delete-task")
async def delete_task(db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin', 'manager')),
                      task_id: int | None = Query(None, description="Search task by id"),
                      title: str = Query("", description="Search task by title")
                      ) -> StatusTasksResponse:

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
async def delete_done_task(db: Session = Depends(get_db),
                            _: User = Depends(require_roles('admin', 'manager')),
                            ) -> StatusTasksResponse:
    
    db_tasks = db.query(Task).filter(Task.status == 'done').all()

    if not db_tasks.count() == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        deleted_count = db_tasks.delete(synchronize_session='fetch')
        db.commit()
        response = StatusTasksResponse(
            status="deleted",
            details=f"Deleted {deleted_count} done tasks: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        response = StatusTasksResponse(
            status="error",
            details=f"Failed to delete deals: {str(e)}"
        )

    response.tasks = TaskRead.model_validate(db_tasks)

    return response

@router.delete("/tasks/delete-expired-task", response_model=StatusTasksResponse, operation_id="delete-expired-tasks")
async def delete_expired_task(db: Session = Depends(get_db),
                              _: User = Depends(require_roles('admin', 'manager')),
                              ) -> StatusTasksResponse:

    now = datetime.now(timezone.utc)  
    db_tasks = db.query(Task).filter(Task.due_date <= now).all()

    if not db_tasks.count() == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        deleted_count = db_tasks.delete(synchronize_session='fetch')
        db.commit()
        response = StatusTasksResponse(
            status="deleted",
            details=f"Deleted {deleted_count} expired tasks: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        response = StatusTasksResponse(
            status="error",
            details=f"Failed to delete deals: {str(e)}"
        )

    response.tasks = TaskRead.model_validate(db_tasks)

    return response
