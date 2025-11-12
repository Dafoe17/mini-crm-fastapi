from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.api.dependencies import Session, get_db 

from src.models import User, Client
from src.schemas.client import ClientRead, ClientCreate


router = APIRouter(tags=['Clients'])


@router.get("/clients/get", response_model=List[ClientRead])
async def get_clients(db: Session = Depends(get_db)) -> List[ClientRead]:
    return db.query(Client).all()

@router.post("/clients/add", response_model=ClientRead)
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

@router.delete("/clients/delete/{client_id}", response_model=List[ClientRead])
async def delete_client(client_id: int, db: Session = Depends(get_db)) -> List[ClientRead]:
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(client)
    db.commit()
    return db.query(Client).all()
