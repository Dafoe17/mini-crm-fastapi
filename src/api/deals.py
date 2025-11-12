from fastapi import APIRouter, HTTPException, Depends
from typing import List
from src.api.dependencies import Session, get_db 

from src.models import Client, Deal
from src.schemas.deal import DealRead, DealCreate

router = APIRouter(tags=['Deals'])

@router.get("/deals/get", response_model=List[DealRead])
async def get_deals(db: Session = Depends(get_db)) -> List[DealRead]:
    return db.query(Deal).all()

@router.post("/deals/add", response_model=DealRead)
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

@router.delete("/users/delete/{deal_id}", response_model=List[DealRead])
async def delete_deal(deal_id: int, db: Session = Depends(get_db)) -> List[DealRead]:
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    db.delete(deal)
    db.commit()
    return db.query(Deal).all()
