from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from src.schemas.deal import DealsListResponse, StatusDealsResponse, DealRead, DealCreate
from src.repositories.deals_repository import DealsRepository
from src.repositories.clients_repository import ClientsRepository
from src.repositories.users_repository import UsersRepository


class DealsService:

    ALLOWED_SORT_FIELDS = {"id", "tittle", "value", "created_at", "updated_at", "closed_at"}

    @staticmethod
    def get_all(
        db: Session,
        current_user,
        skip: int | None,
        limit: int | None,
        search: str | None,
        more_than: int | None,
        less_than: int | None,
        related_to_me: bool | None,
        related_to_user: str | None,
        related_to_client: str | None,
        sort_by: str,
        order: str
    ) -> DealsListResponse:
        
        if sort_by not in DealsService.ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )
        
        filters = []
        
        if related_to_client:
            filters.append(DealsRepository.get_by_client_name(related_to_client))

        if related_to_me:
            related_to_user = current_user.username

        if related_to_user:
            filters.append(DealsRepository.get_by_username(related_to_user))
        
        if search:
            filters.append(DealsRepository.search(search))

        if more_than:
            filters.append(DealsRepository.more_than(more_than))
    
        if less_than:
            filters.append(DealsRepository.less_than(less_than))
        
        query = DealsRepository.apply_filters(db, filters)
        query = DealsRepository.apply_sorting(query, sort_by, order)
        total_deals = DealsRepository.count(query)
        deals = DealsRepository.paginate(query, skip, limit)

        return DealsListResponse(
            total=total_deals,
            skip=skip,
            limit=limit,
            deals=[DealRead.model_validate(deal) for deal in deals]
        )
    
    @staticmethod
    def get_by_date(
        db: Session,
        current_user,
        skip: int | None,
        limit: int | None,
        date_field: str,
        search: str | None,
        more_than: int | None,
        less_than: int | None,
        exact_date: datetime | None,
        earlier_than: datetime | None,
        later_than: datetime | None,
        new: bool,
        related_to_me: bool | None,
        related_to_user: str | None,
        related_to_client: str | None,
        sort_by: str,
        order: str
    ) -> DealsListResponse:

        filters = []

        if related_to_client:
            filters.append(DealsRepository.get_by_client_name(related_to_client))

        if related_to_me:
            related_to_user = current_user.username

        if related_to_user:
            filters.append(DealsRepository.get_by_username(related_to_user))
        
        if search:
            filters.append(DealsRepository.search(query, search))

        if more_than:
            filters.append(DealsRepository.more_than(query, more_than))
    
        if less_than:
            filters.append(DealsRepository.less_than(query, less_than))

        if exact_date:
            filters.append(DealsRepository.exact_date(exact_date, date_field))

        if earlier_than:
            filters.append(DealsRepository.earlier_than(earlier_than, date_field))
        
        if later_than:
            filters.append(DealsRepository.later_than(later_than, date_field))

        if new:
            filters.append(DealsRepository.new(date_field))

        query = DealsRepository.apply_filters(db, filters)
        query = DealsRepository.apply_sorting(query, sort_by, order)
        total_deals = DealsRepository.count(query)
        deals = DealsRepository.paginate(query, skip, limit)

        return DealsListResponse(
            total=total_deals,
            skip=skip,
            limit=limit,
            deals=[DealRead.model_validate(deal) for deal in deals]
        )

    @staticmethod
    def update_deal(
        deal: DealCreate,
        db: Session, 
        current_user,
        deal_id: int | None,
        title: str
        ) -> StatusDealsResponse:
        
        if deal_id:
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        client_id = ClientsRepository.get_by_id(db, db_deal.client_id)
        user_id = UsersRepository.get_by_id(db, client_id.user_id)
        
        if current_user.role == 'manager':
            if user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            created_client = ClientsRepository.update(db, 
                                                    db_deal,
                                                    client_id,
                                                    deal.title,
                                                    deal.status,
                                                    deal.value,
                                                    deal.closed_at)
            
            return StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(created_client)
            )
        except Exception as e:
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change deal: {str(e)}")

    @staticmethod
    def set_status(
        status: str,
        db: Session, 
        current_user,
        deal_id: int | None,
        title: str
        ) -> StatusDealsResponse:
        
        if deal_id:
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        client_id = ClientsRepository.get_by_id(db, db_deal.client_id)
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, client_id.user_id)
            if user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            created_client = ClientsRepository.update(db, 
                                                    db_deal,
                                                    client_id,
                                                    db_deal.title,
                                                    status,
                                                    db_deal.value,
                                                    db_deal.closed_at)
            
            return StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(created_client)
            )
        
        except Exception as e:
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change deal status: {str(e)}")
    
    @staticmethod
    def set_close_date(
        date: datetime,
        db: Session, 
        current_user,
        deal_id: int | None,
        title: str
        ) -> StatusDealsResponse:
        
        if deal_id:
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        db_client = ClientsRepository.get_by_id(db, db_deal.client_id)
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, db_client.user_id)
            if user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            Updated_deal = DealsRepository.update(db, 
                                                    db_deal,
                                                    db_client.id,
                                                    db_deal.title,
                                                    db_deal.status,
                                                    db_deal.value,
                                                    date)
            
            return StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(Updated_deal)
            )
        
        except Exception as e:
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change deal status: {str(e)}")

    @staticmethod
    def add_deal(
        deal: DealCreate,
        db: Session, 
        current_user
        ) -> StatusDealsResponse:
        
        query = DealsRepository.get_by_title(db, deal.title)

        if query:
            raise HTTPException(status_code=400, detail="Deal already exists")
        

        assigned_client = ClientsRepository.get_by_name(db, deal.client_name)

        if not assigned_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, assigned_client.user_id)
            if user_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to create only deals related to your user"""
                )

        try:
            created_deal = DealsRepository.add(db, 
                                               assigned_client.id,
                                               deal.title,
                                               deal.status,
                                               deal.value,
                                               deal.closed_at)
            
            return StatusDealsResponse(
                status="created",
                deals=DealRead.model_validate(created_deal)
            )
        except Exception as e:
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to create deal: {str(e)}")
        
    @staticmethod
    def delete_deal(
        title: str,
        deal_id: int | None,
        db: Session,
        ):

        if deal_id:
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            db_deal = DealsRepository.get_by_title(db, title)

        if not db_deal:
                raise HTTPException(status_code=404, detail="Deal not found")
        
        try:
            deleted_deal = DealsRepository.delete(db, db_deal)
            return StatusDealsResponse(
                status="deleted",
                deals=DealRead.model_validate(deleted_deal)
            )
        except Exception as e:
            raise HTTPException(500, f"Failed to delete deal: {str(e)}")
        
    @staticmethod
    def delete_deal_by_client(
        client_name: str,
        client_id: int | None,
        db: Session,
        ):

        filters = []

        if client_id:
            client = ClientsRepository.get_by_id(db, client_id)
            if not client:
                raise HTTPException(status_code=404, detail="Client not found")
            
            client_name = client.name

        filters.append(DealsRepository.get_by_client_name(client_name))

        query = DealsRepository.apply_filters(db, filters)

        deals_to_delete = query.all()
        if not deals_to_delete:
            raise HTTPException(status_code=404, detail="No deals for this client")
        
        try:
            _ = DealsRepository.delete_group(db, query)
            return StatusDealsResponse(
                status="deleted",
                deals=[DealRead.model_validate(deal_to_delete) for deal_to_delete in deals_to_delete]
            )
        
        except Exception as e:
            raise HTTPException(500, f"Failed to delete deals: {str(e)}")