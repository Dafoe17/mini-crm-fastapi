from sqlalchemy import _or
from sqlalchemy.orm import Session, Query
from src.models import User, Task
from datetime import datetime, timezone

class TasksRepository:

    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Task).filter(Task.id == id).first()
    
    @staticmethod
    def get_by_title(db: Session, title: str):
        return db.query(Task).filter(Task.title == title).first()
    
    @staticmethod
    def get_all_done(db: Session):
        return db.query(Task).filter(Task.status == 'done').all()
    
    @staticmethod
    def get_all_expired(db: Session):
        now = datetime.now(timezone.utc)  
        return db.query(Task).filter(Task.due_date <= now).all()

    @staticmethod
    def get_by_username(db: Session, username: str):
        user_ids = db.query(User.id).filter(User.username.ilike(f"%{username}%")).subquery()
        return Task.user_id.in_(user_ids).all()
    
    @staticmethod
    def search(search: str):
        return _or(
            Task.title.ilike(f"%{search}%"),
            Task.description.ilike(f"%{search}%"),
            Task.status.ilike(f"%{search}%")
            )
    
    @staticmethod
    def apply_filters(db: Session, filters: list):
        query = db.query(Task)
        if filters:
            query = query.filter(*filters)
        return query.all()

    @staticmethod
    def apply_sorting(query, sort_attr, order: str):
        query = query.order_by(sort_attr.desc() if order == "desc" else sort_attr.asc())
        return query

    @staticmethod
    def paginate(query, skip: int | None, limit: int | None) -> list[Task]:
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(query) -> int:
        return query.count()
    
    @staticmethod
    def update(db: Session, 
                    task, 
                    id: int,
                    title: str, 
                    description: str, 
                    status: str,
                    due_date: datetime
                    ) -> Task:
        task.user_id = id
        task.title = title
        task.description = description
        task.status = status
        task.due_date = due_date
        db.commit()
        db.refresh(task)
        return task
    
    @staticmethod
    def add(db : Session, 
            user_id : int,
            title : str,
            description : str,
            status : int,
            due_date : datetime) -> Task:

        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            due_date=due_date
        )

        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(db: Session, task) -> Task:
        db.delete(task)
        db.commit()
        return task
    
    @staticmethod
    def delete_group(db: Session, query: Query) -> list:
        query.delete(synchronize_session='fetch')
        db.commit()
        return query

    @staticmethod
    def rollback(db: Session):
        db.rollback()