from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.api.dependencies import get_db, Session

from src.models import Deal, Task
from src.schemas.task import TaskRead, TaskCreate

router = APIRouter(tags=['Tasks'])

@router.get("/tasks/get", response_model=List[TaskRead])
async def get_tasks(db: Session = Depends(get_db)) -> List[TaskRead]:
    return db.query(Task).all()

@router.post("/tasks/add", response_model=TaskRead)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    db_deal = db.query(Deal).filter(Deal.id == task.deal_id).first()
    if db_deal is None:
        raise HTTPException(status_code=404, detail='Deal not found')
    
    db_task = Task(deal_id=task.deal_id, 
                   title=task.title, 
                   description=task.description, 
                   due_date=task.due_date, 
                   status=task.status)
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except:
        db.rollback() 
    return db_task

@router.delete("/tasks/delete/{task_id}", response_model=List[TaskRead])
async def delete_task(task_id: int, db: Session = Depends(get_db)) -> List[TaskRead]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return db.query(Task).all()
