from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, List, Dict
from sqlalchemy.orm import Session

from models import Base, User, Client, Deal, Task
from database import engine, session_local
from schemas import UserCreate, ClientCreate, DealCreate, TaskCreate, UserRead, ClientRead, DealRead, TaskRead

app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/get", response_model=List[UserRead])
async def get_users(db: Session = Depends(get_db)) -> List[UserRead]:
    return db.query(User).all()

@app.post("/users/add", response_model=UserRead)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    db_user = User(username=user.username, 
                   password_hash=user.password_hash)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        db.rollback() 
    return db_user


@app.get("/clients/get", response_model=List[ClientRead])
async def get_clients(db: Session = Depends(get_db)) -> List[ClientRead]:
    return db.query(Client).all()

@app.post("/clients/add", response_model=ClientRead)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)) -> ClientRead:
    db_user = db.query(User).filter(User.id == client.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail='User not found')
    
    db_client = Client(user_id=client.user_id, 
                       name=client.name, 
                       email=client.email, 
                       phone=client.phone, 
                       notes=client.notes)
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
    except:
        db.rollback() 
    return db_client


@app.get("/deals/get", response_model=List[DealRead])
async def get_deals(db: Session = Depends(get_db)) -> List[DealRead]:
    return db.query(Deal).all()

@app.post("/deals/add", response_model=DealRead)
async def create_client(deal: DealCreate, db: Session = Depends(get_db)) -> DealRead:
    db_client = db.query(Client).filter(Client.id == deal.client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail='Client not found')
    
    db_deal = Deal(client_id=deal.client_id, 
                   title=deal.title, 
                   status=deal.status, 
                   value=deal.value, 
                   created_at=deal.created_at, 
                   closed_at=deal.closed_at)
    try:
        db.add(db_deal)
        db.commit()
        db.refresh(db_deal)
    except:
        db.rollback() 
    return db_deal


@app.get("/tasks/get", response_model=List[TaskRead])
async def get_tasks(db: Session = Depends(get_db)) -> List[TaskRead]:
    return db.query(Task).all()

@app.post("/tasks/add", response_model=TaskRead)
async def create_client(task: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
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
