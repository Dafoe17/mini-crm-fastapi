from fastapi import APIRouter, HTTPException, Depends, Query
from src.api.dependencies import Session, get_db, require_roles

from src.enums import SortOrder
from src.models import User, Client, Deal
from src.schemas.deal import DealRead, DealCreate, DealsListResponse, StatusDealsResponse

router = APIRouter(tags=['Deals'])

@router.get("/deals/get-all", response_model=DealsListResponse, operation_id="get-all-deals")
async def get_all_deals(db: Session = Depends(get_db), 
                          current_user: User = Depends(require_roles('admin', 'manager')),
                          skip: int = Query(None, description="Number of deals to skip"),
                          limit: int = Query(None, description="Number of deals to return"),
                          search: str | None = Query(None, description="Search by title"),
                          bigger_than: int = Query(None, description="Filter deals with value bigger than arg"),
                          less_than: int = Query(None, description="Filter deals with value less than arg"),
                          related_to_curr_user: bool = Query(False, description="Filter deals related to to your user"),
                          related_to_user: str | None = Query(None, description="Filter deals related to user"),
                          related_to_client: str | None = Query(None, description="Filter deals related to clients"),
                          sort_by: str = Query("id", description="Sort by field: id, title, status, value"),
                          order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                          ) -> DealsListResponse:
    
    query = db.query(Deal)

    if related_to_client:
        client_ids = db.query(Client.id).filter(Client.name.islike(f"%{related_to_client}%")).subquery()
        query = query.filter(Deal.client_id.in_(client_ids))

    if related_to_user:
        user_ids = db.query(User.id).filter(User.username.islike(f"%{related_to_user}%")).subquery
        client_ids = db.query(Client.id).filter(Client.user_id.in_(user_ids))
        query = query.filter(Deal.client_id.in_(client_ids))

    if related_to_curr_user:
        user_ids = db.query(User.id).filter(User.username.islike(f"%{current_user.username}%")).subquery
        client_ids = db.query(Client.id).filter(Client.user_id.in_(user_ids))
        query = query.filter(Deal.client_id.in_(client_ids))

    if search:
        query = query.filter(Deal.title.ilike(f"%{search}%"))

    if bigger_than:
        query = db.query(Deal).filter(Deal.value >= bigger_than)
    
    if less_than:
        query = db.query(Deal).filter(Deal.value <= less_than)

    if hasattr(Deal, sort_by):
        sort_attr = getattr(Deal, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_deals = query.count()
    deals = query.offset(skip).limit(limit).all()

    return DealsListResponse(
        total=total_deals,
        skip=skip,
        limit=limit,
        clients=[Deal.model_validate(deal) for deal in deals]
    )

@router.post("/deals/add", response_model=StatusDealsResponse, operation_id="add-deal")
async def add_deal(deal: DealCreate, 
                   db: Session = Depends(get_db),
                   current_user: User = Depends(require_roles('admin', 'manager')),
                   ) -> StatusDealsResponse:
    query = db.query(Deal).filter(Deal.title == deal.title).first()
    if query:
        raise HTTPException(status_code=404, detail="Deal already exists")
    
    if current_user.role == 'manager':
        user_id = current_user.id
        client_names = db.query(Client.name).filter(Client.user_id == user_id)
        if deal.client_name in (client_names):
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to create only deals related to your user"""
            )

    assigned_client = db.query(Client.id).filter(Client.name == deal.client_name).first()
    if not assigned_client:
        raise HTTPException(status_code=404, detail="Client not found")
    user_id = assigned_client.id

    db_deal = Deal(client_id=user_id,
                   title=deal.title,
                   status=deal.status,
                   value=deal.value,
                   closed_at=deal.closed_at)
    
    try:
        db.add(db_deal)
        db.commit()
        db.refresh(db_deal)
        response = StatusDealsResponse(
            status="created",
        )
    
    except Exception as e:
        db.rollback() 
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to create deal: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deal)

    return response
