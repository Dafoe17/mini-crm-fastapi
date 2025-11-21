from src.core.logger import logger
from fastapi import APIRouter, Depends, Query
from src.api.dependencies import Session, get_db, require_roles

from src.services.deals_service import DealsService
from datetime import datetime
from src.enums import SortOrder, DealStatus, DateColumn
from src.models import User
from src.schemas.deal import DealCreate, DealsListResponse, StatusDealsResponse

router = APIRouter(tags=['Deals'])

@router.get("/deals/get-all", response_model=DealsListResponse, operation_id="get-all-deals")
async def get_all_deals(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles('admin', 'manager')),
    skip: int = Query(None, description="Number of deals to skip"),
    limit: int = Query(None, description="Number of deals to return"),
    search: str | None = Query(None, description="Search by title"),
    more_than: int = Query(None, description="Filter deals with value bigger than arg"),
    less_than: int = Query(None, description="Filter deals with value less than arg"),
    related_to_me: bool = Query(False, description="Filter deals related to to your user"),
    related_to_user: str | None = Query(None, description="Filter deals related to user"),
    related_to_client: str | None = Query(None, description="Filter deals related to clients"),
    sort_by: str = Query("id", description="Sort by field: id, title, status, value"),
    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
    ):
    logger.info('User %s requested info about all deals with attributes: ' \
                'skip=%s, limit=%s, search=%s, more_than=%s, less_than=%s, ' \
                'related_to_me=%s, related_to_user=%s, related_to_client=%s, '
                'sort_by=%s, order=%s', 
                current_user.username, skip, limit, search, more_than, less_than, 
                related_to_me, related_to_user, related_to_client, sort_by, order)
    return DealsService.get_all(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        more_than=more_than,
        less_than=less_than,
        related_to_me=related_to_me,
        related_to_user=related_to_user,
        related_to_client=related_to_client,
        sort_by=sort_by,
        order=order
    )

@router.get("/deals/get-by-date", response_model=DealsListResponse, operation_id="get-by-date")
async def get_by_date(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    skip: int = Query(None, description="Number of deals to skip"),
    limit: int = Query(None, description="Number of deals to return"),
    date_field: DateColumn = Query("created_at" , 
                                   description="Choose date column: created_at, updated_at or closed_at"),
    search: str | None = Query(None, description="Search by title"),
    more_than: int = Query(None, description="Filter deals with value bigger than arg"),
    less_than: int = Query(None, description="Filter deals with value less than arg"),
    exact_date: datetime | None = Query(None, description="Search by exact day"),
    earlier_than: datetime | None = Query(None, description="Filter deals created earlier than arg"),
    later_than: datetime | None = Query(None, description="Filter deals created later than arg"),
    new: bool = Query(False, description="Filter deals created earlier this mounth"),
    related_to_me: bool = Query(False, description="Filter deals related to to your user"),
    related_to_user: str | None = Query(None, description="Filter deals related to user"),
    related_to_client: str | None = Query(None, description="Filter deals related to clients"),
    sort_by: str = Query("id", description="Sort by field: id, title, status, value"),
    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
    ):
    logger.info('User %s requested info about all deals by date with attributes: ' \
                'skip=%s, limit=%s, date_field=%s, search=%s, more_than=%s, less_than=%s, ' \
                'exact_date=%s, related_to_me=%s, related_to_user=%s, related_to_client=%s, '
                'sort_by=%s, order=%s', 
                current_user.username, skip, limit, date_field, search, more_than, less_than, 
                exact_date, related_to_me, related_to_user, related_to_client, sort_by, order)
    return DealsService.get_by_date(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        date_field=date_field,
        search=search,
        more_than=more_than,
        less_than=less_than,
        exact_date=exact_date,
        earlier_than=earlier_than,
        later_than=later_than,
        new=new,
        related_to_me=related_to_me,
        related_to_user=related_to_user,
        related_to_client=related_to_client,
        sort_by=sort_by,
        order=order
    )

@router.patch("/deals/patch/set-close-date", response_model=StatusDealsResponse, operation_id="set-close-date")
async def set_close_date(
    date: datetime = Query('', description="Set exact day"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    deal_id: int | None = Query(None, description="Search deal by id"),
    title: str = Query("", description="Search deal by title"),
    ):
    logger.info('User %s requested set close date (%s) for deal (%s, %s)', 
                current_user.username, date, deal_id, title)
    return DealsService.set_close_date(
        date=date,
        db=db,
        current_user=current_user,
        deal_id=deal_id,
        title=title
    )

@router.patch("/deals/patch/set-status", response_model=StatusDealsResponse, operation_id="set-status")
async def set_status(
    status: DealStatus = Query("new", description="Set new status: new, in_progress or closed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    deal_id: int | None = Query(None, description="Search deal by id"),
    title: str = Query("", description="Search deal by title"),
    ):
    logger.info('User %s requested set status (%s) for deal (%s, %s)', 
                current_user.username, status, deal_id, title)
    return DealsService.set_status(
        status=status,
        db=db,
        current_user=current_user,
        deal_id=deal_id,
        title=title
    )

@router.post("/deals/add", response_model=StatusDealsResponse, operation_id="add-deal")
async def add_deal(
    deal: DealCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    ):
    logger.info('User %s requested create deal (%s)', 
                current_user.username, deal.title)
    return DealsService.add_deal(
        deal=deal,
        db=db,
        current_user=current_user
    )

@router.put("/deals/update", response_model=StatusDealsResponse, operation_id="update-deal")
async def update_deal(
    deal: DealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    deal_id: int | None = Query(None, description="Search deal by id"),
    title: str = Query("", description="Search deal by title"),
    ):
    logger.info('User %s requested update deal (%s, %s)', 
                current_user.username, deal_id, title)
    return DealsService.update_deal(
        deal=deal,
        db=db,
        current_user=current_user,
        deal_id=deal_id,
        title=title
    )

@router.delete("/deals/delete", response_model=StatusDealsResponse, operation_id="delete-deal")
async def delete_deal(title: str = Query("", description="Delete by title"),
                      deal_id: int | None = Query(None, description="Delete by id"),
                      db: Session = Depends(get_db),
                      current_user: User = Depends(require_roles('admin')),
                      ):
    logger.info('User %s requested delete deal (%s, %s)', 
                current_user.username, deal_id, title)
    return DealsService.delete_deal(
        title=title,
        deal_id=deal_id,
        db=db
    )

@router.delete("/deals/delete-by-client", response_model=StatusDealsResponse, operation_id="delete-by-client")
async def delete_by_client(
    client_name: str = Query("", description="Delete by client name"),
    client_id: int | None = Query(None, description="Delete by client id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin')),
    ):
    logger.info('User %s requested delete deal by client (%s, %s)', 
                current_user.username, client_id, client_name)
    return DealsService.delete_deal_by_client(
        client_name=client_name,
        client_id=client_id,
        db=db
    )
