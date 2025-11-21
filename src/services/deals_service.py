from src.core.logger import logger
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
        
        logger.debug('Trying to get all deals')
        if sort_by not in DealsService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )
        
        filters = []
        
        if related_to_client:
            logger.debug('Add related_to_client filter (%s)', related_to_client)
            filters.append(DealsRepository.get_by_client_name(related_to_client))

        if related_to_me:
            logger.debug('Add related_to_me filter (%s)', related_to_me)
            related_to_user = current_user.username

        if related_to_user:
            logger.debug('Add related_to_user filter (%s)', related_to_user)
            filters.append(DealsRepository.get_by_username(related_to_user))
        
        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(DealsRepository.search(search))

        if more_than:
            logger.debug('Add more_than filter (%s)', more_than)
            filters.append(DealsRepository.more_than(more_than))
    
        if less_than:
            logger.debug('Add less_than filter (%s)', less_than)
            filters.append(DealsRepository.less_than(less_than))
        
        logger.debug('Applying filters')
        query = DealsRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = DealsRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total_deals = DealsRepository.count(query)
        logger.debug('Paginating')
        deals = DealsRepository.paginate(query, skip, limit)

        logger.debug('Forming DealsListResponse')
        response = DealsListResponse(
            total=total_deals,
            skip=skip,
            limit=limit,
            deals=[DealRead.model_validate(deal) for deal in deals]
        )
        logger.info('Success')
        return response
    
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

        logger.debug('Trying to get all deals by datefield')
        if sort_by not in DealsService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )
        
        filters = []

        if related_to_client:
            logger.debug('Add related_to_client filter (%s)', related_to_client)
            filters.append(DealsRepository.get_by_client_name(related_to_client))

        if related_to_me:
            logger.debug('Add related_to_me filter (%s)', related_to_me)
            related_to_user = current_user.username

        if related_to_user:
            logger.debug('Add related_to_user filter (%s)', related_to_user)
            filters.append(DealsRepository.get_by_username(related_to_user))
        
        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(DealsRepository.search(query, search))

        if more_than:
            logger.debug('Add more_than filter (%s)', more_than)
            filters.append(DealsRepository.more_than(query, more_than))
    
        if less_than:
            logger.debug('Add less_than filter (%s)', less_than)
            filters.append(DealsRepository.less_than(query, less_than))

        if exact_date:
            logger.debug('Add exact_date filter (%s)', exact_date)
            filters.append(DealsRepository.exact_date(exact_date, date_field))

        if earlier_than:
            logger.debug('Add earlier_than filter (%s)', earlier_than)
            filters.append(DealsRepository.earlier_than(earlier_than, date_field))
        
        if later_than:
            logger.debug('Add later_than filter (%s)', later_than)
            filters.append(DealsRepository.later_than(later_than, date_field))

        if new:
            logger.debug('Add new filter (%s)', new)
            filters.append(DealsRepository.new(date_field))

        logger.debug('Applying filters')
        query = DealsRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = DealsRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total_deals = DealsRepository.count(query)
        logger.debug('Paginating')
        deals = DealsRepository.paginate(query, skip, limit)

        logger.debug('Forming DealsListResponse')
        response = DealsListResponse(
            total=total_deals,
            skip=skip,
            limit=limit,
            deals=[DealRead.model_validate(deal) for deal in deals]
        )
        logger.info('Success')
        return response

    @staticmethod
    def update_deal(
        deal: DealCreate,
        db: Session, 
        current_user,
        deal_id: int | None,
        title: str
        ) -> StatusDealsResponse:
        
        if deal_id:
            logger.debug('Searching by id')
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            logger.debug('Searching by title')
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            logger.warning('Deal not found')
            raise HTTPException(status_code=404, detail="Deal not found")
        
        client_id = ClientsRepository.get_by_id(db, db_deal.client_id)
        user_id = UsersRepository.get_by_id(db, client_id.user_id)
        
        if current_user.role == 'manager':
            if user_id != current_user.id:
                logger.warning('Access denied')
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            logger.debug('Trying update deal')
            updated_deal = ClientsRepository.update(db, 
                                                    db_deal,
                                                    client_id,
                                                    deal.title,
                                                    deal.status,
                                                    deal.value,
                                                    deal.closed_at)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(updated_deal)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to change deal')
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
            logger.debug('Searching by id')
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            logger.debug('Searching by title')
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            logger.warning('Deal not found')
            raise HTTPException(status_code=404, detail="Deal not found")
        
        client_id = ClientsRepository.get_by_id(db, db_deal.client_id)
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, client_id.user_id)
            if user_id != current_user.id:
                logger.warning('Access denied')
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            logger.debug('Trying set deal status')
            updated_deal = DealsRepository.update(db, 
                                                    db_deal,
                                                    client_id.id,
                                                    db_deal.title,
                                                    status,
                                                    db_deal.value,
                                                    db_deal.closed_at)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(updated_deal)
            )
            logger.info('Success')
            return response

        except Exception as e:
            logger.error('Failed to change deal status')
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
            logger.debug('Searching by id')
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            logger.debug('Searching by title')
            db_deal = DealsRepository.get_by_title(db, title)
        
        if not db_deal:
            logger.warning('Deal not found')
            raise HTTPException(status_code=404, detail="Deal not found")
        
        db_client = ClientsRepository.get_by_id(db, db_deal.client_id)
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, db_client.user_id)
            if user_id != current_user.id:
                logger.warning('Access denied')
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to update only deals related to your user"""
                )

        try:
            logger.debug('Trying set deal close date')
            updated_deal = DealsRepository.update(db, 
                                                    db_deal,
                                                    db_client.id,
                                                    db_deal.title,
                                                    db_deal.status,
                                                    db_deal.value,
                                                    date)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="changed",
                deals=DealRead.model_validate(updated_deal)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to change deal')
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change deal status: {str(e)}")

    @staticmethod
    def add_deal(
        deal: DealCreate,
        db: Session, 
        current_user
        ) -> StatusDealsResponse:
        
        logger.debug('Searching by title')
        query = DealsRepository.get_by_title(db, deal.title)

        if query:
            logger.warning('Deal already exists')
            raise HTTPException(status_code=400, detail="Deal already exists")
        
        assigned_client = ClientsRepository.get_by_name(db, deal.client_name)

        if not assigned_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")
        
        if current_user.role == 'manager':
            user_id = UsersRepository.get_by_id(db, assigned_client.user_id)
            if user_id != current_user.id:
                logger.warning('Access denied')
                raise HTTPException(
                    status_code=403,
                    detail=f""""Access denied. 
                    Your role able to create only deals related to your user"""
                )

        try:
            logger.debug('Trying create deal')
            created_deal = DealsRepository.add(db, 
                                               assigned_client.id,
                                               deal.title,
                                               deal.status,
                                               deal.value,
                                               deal.closed_at)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="created",
                deals=DealRead.model_validate(created_deal)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to create deal')
            DealsRepository.rollback(db)
            raise HTTPException(500, f"Failed to create deal: {str(e)}")
        
    @staticmethod
    def delete_deal(
        title: str,
        deal_id: int | None,
        db: Session,
        ):

        if deal_id:
            logger.debug('Searching by id')
            db_deal = DealsRepository.get_by_id(db, deal_id)
        else:
            logger.debug('Searching by title')
            db_deal = DealsRepository.get_by_title(db, title)

        if not db_deal:
                logger.warning('Deal not found')
                raise HTTPException(status_code=404, detail="Deal not found")
        
        try:
            logger.debug('Trying delete deal')
            deleted_deal = DealsRepository.delete(db, db_deal)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="deleted",
                deals=DealRead.model_validate(deleted_deal)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete deal')
            raise HTTPException(500, f"Failed to delete deal: {str(e)}")
        
    @staticmethod
    def delete_deal_by_client(
        client_name: str,
        client_id: int | None,
        db: Session,
        ):

        filters = []

        if client_id:
            logger.debug('Searching by client_id')
            client = ClientsRepository.get_by_id(db, client_id)
            if not client:
                logger.warning('Client not found')
                raise HTTPException(status_code=404, detail="Client not found")
            
            client_name = client.name

        logger.debug('Searching by client_name')
        filters.append(DealsRepository.get_by_client_name(client_name))

        logger.debug('Applying filters')
        query = DealsRepository.apply_filters(db, filters)
        deals_to_delete = query.all()

        if not deals_to_delete:
            logger.warning('No deals for this client')
            raise HTTPException(status_code=404, detail="No deals for this client")
        
        try:
            logger.debug('Trying delete deals by client')
            _ = DealsRepository.delete_group(db, query)
            logger.debug('Forming StatusDealsResponse')
            response = StatusDealsResponse(
                status="deleted",
                deals=[DealRead.model_validate(deal_to_delete) for deal_to_delete in deals_to_delete]
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete deals by client')
            raise HTTPException(500, f"Failed to delete deals: {str(e)}")
        