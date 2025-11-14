from fastapi import APIRouter, HTTPException, Depends, Query
from src.api.dependencies import Session, get_db, require_roles

from datetime import datetime, timedelta, timezone
from src.enums import SortOrder, DealStatus
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
        deals=[Deal.model_validate(deal) for deal in deals]
    )

@router.get("/deals/get-by-created-date", response_model=DealsListResponse, operation_id="get-by-created-date")
async def get_by_create_date(db: Session = Depends(get_db),
                            current_user: User = Depends(require_roles('admin', 'manager')),
                            skip: int = Query(None, description="Number of deals to skip"),
                            limit: int = Query(None, description="Number of deals to return"),
                            exact_date: datetime | None = Query(None, description="Search by exact day"),
                            earlier_than: datetime | None = Query(None, description="Filter deals created earlier than arg"),
                            later_than: datetime | None = Query(None, description="Filter deals created later than arg"),
                            new: bool = Query(False, description="Filter deals created earlier this mounth"),
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

    if exact_date:
        start_of_day = datetime.combine(exact_date.date(), datetime.min.time())
        end_of_day = datetime.combine(exact_date.date(), datetime.max.time())
        query = query.filter(Deal.created_at >= start_of_day, Deal.created_at <= end_of_day)

    if earlier_than:
        query = query.filter(Deal.created_at >= earlier_than)
    
    if later_than:
        query = query.filter(Deal.created_at >= later_than)

    if new:
        today = datetime.today()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        end_of_month = next_month - timedelta(seconds=1)

        query = query.filter(Deal.created_at >= start_of_month, Deal.created_at <= end_of_month)
    
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
        deals=[DealRead.model_validate(deal) for deal in deals]
    )

@router.get("/deals/get-by-updated-date", response_model=DealsListResponse, operation_id="get-by-updated-date")
async def get_by_update_date(db: Session = Depends(get_db),
                            current_user: User = Depends(require_roles('admin', 'manager')),
                            skip: int = Query(None, description="Number of deals to skip"),
                            limit: int = Query(None, description="Number of deals to return"),
                            exact_date: datetime | None = Query(None, description="Search by exact day"),
                            earlier_than: datetime | None = Query(None, description="Filter deals updated earlier than arg"),
                            later_than: datetime | None = Query(None, description="Filter deals updated later than arg"),
                            new: bool = Query(False, description="Filter deals updated earlier this mounth"),
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

    if exact_date:
        start_of_day = datetime.combine(exact_date.date(), datetime.min.time())
        end_of_day = datetime.combine(exact_date.date(), datetime.max.time())
        query = query.filter(Deal.updated_at >= start_of_day, Deal.updated_at <= end_of_day)

    if earlier_than:
        query = query.filter(Deal.updated_at >= earlier_than)
    
    if later_than:
        query = query.filter(Deal.updated_at >= later_than)

    if new:
        today = datetime.today()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        end_of_month = next_month - timedelta(seconds=1)

        query = query.filter(Deal.updated_at >= start_of_month, Deal.updated_at <= end_of_month)
    
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
        deals=[DealRead.model_validate(deal) for deal in deals]
    )

@router.get("/deals/get-by-closed-date", response_model=DealsListResponse, operation_id="get-by-closed-date")
async def get_by_closed_date(db: Session = Depends(get_db),
                            current_user: User = Depends(require_roles('admin', 'manager')),
                            skip: int = Query(None, description="Number of deals to skip"),
                            limit: int = Query(None, description="Number of deals to return"),
                            exact_date: datetime | None = Query(None, description="Search by exact day"),
                            earlier_than: datetime | None = Query(None, description="Filter deals closed earlier than arg"),
                            later_than: datetime | None = Query(None, description="Filter deals closed later than arg"),
                            soon: bool = Query(False, description="Filter deals closed this mounth"),
                            expired: bool = Query(False, description="Filter closed deals"),
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

    if exact_date:
        start_of_day = datetime.combine(exact_date.date(), datetime.min.time())
        end_of_day = datetime.combine(exact_date.date(), datetime.max.time())
        query = query.filter(Deal.closed_at >= start_of_day, Deal.closed_at <= end_of_day)

    if earlier_than:
        query = query.filter(Deal.closed_at >= earlier_than)
    
    if later_than:
        query = query.filter(Deal.closed_at >= later_than)

    if soon:
        today = datetime.today()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = today.replace(month=today.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        end_of_month = next_month - timedelta(microseconds=1)
        query = query.filter(Deal.closed_at >= start_of_month, Deal.closed_at <= end_of_month)
        
        if hasattr(Deal, sort_by):
            sort_attr = getattr(Deal, sort_by)
            query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
        else:
            raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")
        
    if expired:
        now = datetime.now(timezone.utc)  
        query = query.filter(Deal.closed_at <= now)

    total_deals = query.count()
    deals = query.offset(skip).limit(limit).all()

    return DealsListResponse(
        total=total_deals,
        skip=skip,
        limit=limit,
        deals=[DealRead.model_validate(deal) for deal in deals]
    )

@router.patch("/deals/patch/set-close-date", response_model=StatusDealsResponse, operation_id="set-close-date")
async def set_close_date(date: datetime = Query('', description="Set exact day"),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(require_roles('admin', 'manager')),
                        deal_id: int | None = Query(None, description="Search deal by id"),
                        title: str = Query("", description="Search deal by title"),
                        ) -> StatusDealsResponse:
    if deal_id:
        db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    else:
        db_deal = db.query(Deal).filter((Deal.title.ilike(f"%{title}%"))).first()
    
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    client_id = db.query(Client.user_id).filter(Client.id == db_deal.client_id).first()
    user_id = db.query(User.id).filter(User.id == client_id[0]).first()
    
    if current_user.role == 'manager':
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to update only deals related to your user"""
            )

    db_deal.closed_at = date

    try:
        db.commit()
        db.refresh(db_deal)
        response = StatusDealsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to change date from deal: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deal)

    return response

@router.patch("/deals/patch/set_status", response_model=DealsListResponse, operation_id="set_status")
async def set_status(status: DealStatus = Query("new", description="Set new status: new, in_progress or closed"),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(require_roles('admin', 'manager')),
                    deal_id: int | None = Query(None, description="Search deal by id"),
                    title: str = Query("", description="Search deal by title"),
                    ) -> StatusDealsResponse:
    if deal_id:
        db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    else:
        db_deal = db.query(Deal).filter((Deal.title.ilike(f"%{title}%"))).first()
    
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    client_id = db.query(Client.user_id).filter(Client.id == db_deal.client_id).first()
    user_id = db.query(User.id).filter(User.id == client_id[0]).first()
    
    if current_user.role == 'manager':
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to do only deals related to your user"""
            )

    db_deal.status = status

    try:
        db.commit()
        db.refresh(db_deal)
        response = StatusDealsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to change status from deal: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deal)

    return response

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

@router.put("/deals/update", response_model=StatusDealsResponse, operation_id="update-deal")
async def update_deal(deal: DealCreate,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(require_roles('admin', 'manager')),
                     deal_id: int | None = Query(None, description="Search deal by id"),
                     title: str = Query("", description="Search deal by title"),
                     ) -> StatusDealsResponse:
    if deal_id:
        db_deal = db.query(Deal).filter(Deal.id == deal_id).first()
    else:
        db_deal = db.query(Deal).filter((Deal.title.ilike(f"%{title}%"))).first()
    
    if not db_deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    client_id = db.query(Client.user_id).filter(Client.id == db_deal.client_id).first()
    user_id = db.query(User.id).filter(User.id == client_id[0]).first()
    
    if current_user.role == 'manager':
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to update only deals related to your user"""
            )

    db_deal.client_name = deal.client_name
    db_deal.title = deal.status
    db_deal.closed_at = deal.closed_at
    db_deal.value = deal.value

    try:
        db.commit()
        db.refresh(db_deal)
        response = StatusDealsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to change deal: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deal)

    return response

@router.delete("/deals/delete", response_model=StatusDealsResponse, operation_id="delete-deal")
async def delete_deal(title: str = Query("", description="Delete by title"),
                      deal_id: int | None = Query(None, description="Delete by id"),
                      db: Session = Depends(get_db),
                      _: User = Depends(require_roles('admin')),
                      ) -> StatusDealsResponse:
    if deal_id:
        db_deal = db.query(Deal).filter((Deal.id == deal_id)).first()
    else:
        db_deal = db.query(Deal).filter((Deal.title.ilike(f"%{title}%"))).first()

    if not db_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
    
    try:
        db.delete(db_deal)
        db.commit()
        response = StatusDealsResponse(
            status="deleted",
        )
    except Exception as e:
        db.rollback()
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to delete client: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deal)

    return response

@router.delete("/deals/delete-by-client", response_model=StatusDealsResponse, operation_id="delete-by-client")
async def delete_by_client(client_name: str = Query("", description="Delete by title"),
                            client_id: int | None = Query(None, description="Delete by id"),
                            db: Session = Depends(get_db),
                            _: User = Depends(require_roles('admin')),
                            ) -> StatusDealsResponse:
    if client_id:
        db_deals = db.query(Deal).filter((Deal.client_id == client_id))
    else:
        client_id = db.query(Client.id).filter((Client.name == client_name)).first()[0]
        if not client_id:
            raise HTTPException(status_code=404, detail="Client not found")
        db_deals = db.query(Deal).filter((Deal.client_id == client_id)).all()
    
    if db_deals.count() == 0:
        raise HTTPException(status_code=404, detail="Deals not found")
    
    try:
        deleted_count = db_deals.delete(synchronize_session='fetch')
        db.commit()
        response = StatusDealsResponse(
            status="deleted",
            details=f"Deleted {deleted_count} deals: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        response = StatusDealsResponse(
            status="error",
            details=f"Failed to delete deals: {str(e)}"
        )

    response.deals = DealRead.model_validate(db_deals)

    return response
