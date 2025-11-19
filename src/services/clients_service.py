from src.core.logger import logger
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.client import ClientsListResponse, StatusClientsResponse, ClientRead, ClientCreate
from src.repositories.clients_repository import ClientsRepository
from src.repositories.users_repository import UsersRepository


class ClientsService:

    ALLOWED_SORT_FIELDS = {"id", "name", "email", "phone"}

    @staticmethod
    def get_all(
        db: Session,
        current_user,
        skip: int | None,
        limit: int | None,
        related_to_me: bool | None,
        related_to_user: str | None,
        search: str | None,
        sort_by: str,
        order: str
    ) -> ClientsListResponse:

        logger.debug('Trying to get all clients')
        if sort_by not in ClientsService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        filters = []

        if related_to_me:
            logger.debug('Add related_to_me filter (%s)', related_to_me)
            related_to_user = current_user.username
            
        if related_to_user:
            logger.debug('Add related_to_user filter (%s)', related_to_user)
            filters.append(ClientsRepository.filter_related_to_user(db, related_to_user))
        
        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(ClientsRepository.search(search))        

        logger.debug('Applying filters')
        query = ClientsRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = ClientsRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total_clients = ClientsRepository.count(query)
        logger.debug('Paginating')
        clients = ClientsRepository.paginate(query, skip, limit)

        logger.debug('Forming ClientsListResponse')
        response = ClientsListResponse(
            total=total_clients,
            skip=skip,
            limit=limit,
            clients=[ClientRead.model_validate(client) for client in clients]
        )
        logger.info('Success')
        return response
    
    @staticmethod
    def get_unassigned_clients(
        db: Session,
        skip: int | None,
        limit: int | None,
        search: str | None,
        sort_by: str,
        order: str
    ) -> ClientsListResponse:

        logger.debug('Trying to get unassigned clients')
        if sort_by not in ClientsService.ALLOWED_SORT_FIELDS:
            logger.warning('Invalid sort field %s', sort_by)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        filters = []

        logger.debug('Add unassigned clients filter')
        filters.append(ClientsRepository.get_unassign())

        if search:
            logger.debug('Add search filter (%s)', search)
            filters.append(ClientsRepository.search(search))     

        logger.debug('Applying filters')
        query = ClientsRepository.apply_filters(db, filters)
        logger.debug('Applying sorting')
        query = ClientsRepository.apply_sorting(query, sort_by, order)
        logger.debug('Counting total items')
        total_clients = ClientsRepository.count(query)
        logger.debug('Paginating')
        clients = ClientsRepository.paginate(query, skip, limit)

        logger.debug('Forming ClientsListResponse')
        response = ClientsListResponse(
            total=total_clients,
            skip=skip,
            limit=limit,
            clients=[ClientRead.model_validate(client) for client in clients]
        )
        logger.info('Success')
        return response
    
    @staticmethod
    def take_unassigned_client(
        db: Session, 
        current_user,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        
        if client_id:
            logger.debug('Searching by id')
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            logger.debug('Searching by client_name')
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")
        
        if db_client.user_id:
            logger.warning('Client %s is already assigned.', db_client.name)
            raise HTTPException(status_code=400, detail=f"Client {db_client.name} is already assigned.")
    
        try:
            logger.debug('Trying to take unassigned client')
            taken_client = ClientsRepository.take_client(db, db_client, current_user.id)
            logger.debug('Forming StatusClientsResponse')
            responce = StatusClientsResponse(
                status="changed",
                clients=ClientRead.model_validate(taken_client)
            )
            logger.info('Success')
            return responce
        except Exception as e:
            logger.error('Failed to take client: %s', str(e))
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to take client: {str(e)}")
        
    @staticmethod
    def delegete_unassigned_client(
        db: Session, 
        username: str,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            logger.debug('Searching by id')
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            logger.debug('Searching by client_name')
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")
        
        assigned_user = UsersRepository.get_by_username(db, username)
        if not assigned_user:
            logger.warning('Client %s is already assigned.', db_client.name)
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            logger.debug('Trying to delegete client')
            delegeted_user = ClientsRepository.take_client(db, db_client, assigned_user.id)
            logger.debug('Forming StatusClientsResponse')
            responce = StatusClientsResponse(
                status="changed",
                clients=ClientRead.model_validate(delegeted_user)
            )
            logger.info('Success')
            return responce
        except Exception as e:
            logger.error('Failed to delegete client: %s', str(e))
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to delegete client: {str(e)}")
    
    @staticmethod
    def discharge(
        db: Session, 
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            logger.debug('Searching by id')
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            logger.debug('Searching by client_name')
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")
        
        try:
            logger.debug('Trying to discharge client')
            discharged_client = ClientsRepository.take_client(db, db_client, None)
            logger.debug('Forming StatusClientsResponse')
            response = StatusClientsResponse(
                status="changed",
                clients=ClientRead.model_validate(discharged_client)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to discharge client: %s', str(e))
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to discharge client: {str(e)}")
    
    @staticmethod
    def add_client(
        client: ClientCreate,
        db: Session, 
        current_user
        ) -> StatusClientsResponse:
        
        logger.debug('Searching by client_name')
        query = ClientsRepository.get_by_name(db, client.name)

        if query:
            logger.warning('Client already exists')
            raise HTTPException(status_code=400, detail="Client already exists")
        
        logger.debug('Getting assigned user')
        assigned_user = UsersRepository.get_by_username(db, client.user_name)

        if current_user.role == 'manager' and assigned_user.id != current_user.id:
            logger.warning('Access denied')
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to create only clients related to your user"""
            )
        
        if not assigned_user:
            logger.warning('User not found')
            raise HTTPException(status_code=404, detail="User not found")

        try:
            logger.debug('Trying to take add client')
            created_client = ClientsRepository.add(db, 
                                                   assigned_user.id, 
                                                   client.name,
                                                   client.email,
                                                   client.phone,
                                                   client.notes)
            logger.debug('Trying to take add client')
            response = StatusClientsResponse(
                status="created",
                clients=ClientRead.model_validate(created_client)
            ) 
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to create client')
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to create client: {str(e)}")

    @staticmethod
    def update_client(
        client: ClientCreate,
        db: Session, 
        current_user,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            logger.debug('Searching by id')
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            logger.debug('Searching by client_name')
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")
        
        logger.debug('Getting assigned user')
        assigned_user = UsersRepository.get_by_username(db, client.user_name)

        if current_user.role == 'manager' and assigned_user.id != current_user.id:
            logger.warning('Access denied')
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to update only clients related to your user"""
            )
        
        if not assigned_user:
            logger.warning('User not found')
            raise HTTPException(status_code=404, detail="User not found")

        try:
            logger.debug('Trying update client')
            updated_client = ClientsRepository.update(db, 
                                                   db_client,
                                                   assigned_user.id, 
                                                   client.name,
                                                   client.email,
                                                   client.phone,
                                                   client.notes)
            logger.debug('Forming StatusClientsResponse')
            response = StatusClientsResponse(
                status="changed",
                clients=ClientRead.model_validate(updated_client)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to change user')
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change user: {str(e)}")

    @staticmethod
    def delete_client(
        name: str, 
        db: Session,
        ) -> StatusClientsResponse:
        
        logger.debug('Searching by client name')
        db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            logger.warning('Client not found')
            raise HTTPException(status_code=404, detail="Client not found")

        try:
            logger.debug('Trying to delete client')
            deleted_client = ClientsRepository.delete(db, db_client)
            logger.debug('Forming StatusClientsResponse')
            response = StatusClientsResponse(
                status="deleted",
                clients=ClientRead.model_validate(deleted_client)
            )
            logger.info('Success')
            return response
        except Exception as e:
            logger.error('Failed to delete client: %s', str(e))
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete client: {str(e)}")
