from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.schemas.client import ClientsListResponse, StatusClientsResponse, ClientRead, ClientCreate
from src.repositories.clients_repository import ClientsRepository
from src.repositories.users_repository import UsersRepository
from src.enums import SortOrder


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
        order: SortOrder,
    ) -> ClientsListResponse:

        if sort_by not in ClientsService.ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        query = ClientsRepository.base_query(db)

        if related_to_me:
            query = ClientsRepository.filter_related_to_me(query, current_user)

        if related_to_user:
            query = ClientsRepository.filter_related_to_user(query, related_to_user)
        
        if search:
            query = ClientsRepository.search(query, search)        

        query = ClientsRepository.apply_sorting(query, sort_by, order)
        total_clients = ClientsRepository.count(query)
        clients = ClientsRepository.paginate(query, skip, limit)

        return ClientsListResponse(
            total=total_clients,
            skip=skip,
            limit=limit,
            clients=[ClientRead.model_validate(client) for client in clients]
        )
    
    @staticmethod
    def get_unassigned_clients(
        db: Session,
        skip: int | None,
        limit: int | None,
        search: str | None,
        sort_by: str,
        order: SortOrder,
    ) -> ClientsListResponse:

        if sort_by not in ClientsService.ALLOWED_SORT_FIELDS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort field: {sort_by}"
            )

        query = ClientsRepository.get_unassign(db)

        if search:
            query = ClientsRepository.search(query, search)        

        query = ClientsRepository.apply_sorting(query, sort_by, order)
        total_clients = ClientsRepository.count(query)
        clients = ClientsRepository.paginate(query, skip, limit)

        return ClientsListResponse(
            total=total_clients,
            skip=skip,
            limit=limit,
            clients=[ClientRead.model_validate(client) for client in clients]
        )
    
    @staticmethod
    def take_unassigned_client(
        db: Session, 
        current_user,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        if db_client.user_id:
            raise HTTPException(status_code=400, detail=f"Client {db_client.name} is already assigned.")
    
        try:
            taken_user = ClientsRepository.take_client(db, db_client, current_user.id)
            return StatusClientsResponse(
                status="changed",
                users=ClientRead.model_validate(taken_user)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to take user: {str(e)}")
        
    @staticmethod
    def delegete_unassigned_client(
        db: Session, 
        username: str,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        assigned_user = UsersRepository.get_by_username(db, username)
        if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            delegeted_user = ClientsRepository.take_client(db, db_client, assigned_user.id)
            return StatusClientsResponse(
                status="changed",
                users=ClientRead.model_validate(delegeted_user)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to delegete user: {str(e)}")
    
    @staticmethod
    def discharge(
        db: Session, 
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        try:
            discharged_client = ClientsRepository.take_client(db, db_client, None)
            return StatusClientsResponse(
                status="changed",
                users=ClientRead.model_validate(discharged_client)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to discharge user: {str(e)}")
    
    @staticmethod
    def add_client(
        client: ClientCreate,
        db: Session, 
        current_user
        ) -> StatusClientsResponse:
        
        query = ClientsRepository.get_by_name(db, client.name)

        if query:
            raise HTTPException(status_code=400, detail="Client already exists")
        
        assigned_user = UsersRepository.get_by_username(client.user_name)

        if current_user.role == 'manager' and assigned_user.id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to create only clients related to your user"""
            )
        
        if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            created_client = ClientsRepository.add(db, 
                                                   assigned_user.id, 
                                                   client.name,
                                                   client.email,
                                                   client.phone,
                                                   client.notes)
            return StatusClientsResponse(
                status="created",
                users=ClientRead.model_validate(created_client)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to create user: {str(e)}")

    @staticmethod
    def update_client(
        client: ClientCreate,
        db: Session, 
        current_user,
        client_id: int | None,
        name: str | None,
        ) -> StatusClientsResponse:
        
        if client_id:
            db_client = ClientsRepository.get_by_id(db, client_id)
        else:
            db_client = ClientsRepository.get_by_name(db, name)

        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        assigned_user = UsersRepository.get_by_username(client.user_name)

        if current_user.role == 'manager' and assigned_user.id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to update only clients related to your user"""
            )
        
        if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            updated_client = ClientsRepository.update(db, 
                                                   db_client,
                                                   assigned_user.id, 
                                                   client.name,
                                                   client.email,
                                                   client.phone,
                                                   client.notes)
            return StatusClientsResponse(
                status="changed",
                users=ClientRead.model_validate(updated_client)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to change user: {str(e)}")

    @staticmethod
    def delete_client(
        name: str, 
        db: Session,
        ) -> StatusClientsResponse:
        
        db_client = ClientsRepository.get_by_name(name)

        if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")

        try:
            deleted_client = ClientsRepository.delete(db, db_client)
            return StatusClientsResponse(
                status="deleted",
                users=ClientRead.model_validate(deleted_client)
            )
        except Exception as e:
            ClientsRepository.rollback(db)
            raise HTTPException(500, f"Failed to delete user: {str(e)}")
