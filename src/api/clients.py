from src.core.logger import logger
from fastapi import APIRouter, Query, Depends
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.services.clients_service import ClientsService
from src.enums import SortOrder
from src.models import User
from src.schemas.client import ClientCreate, ClientsListResponse, StatusClientsResponse


router = APIRouter(tags=['Clients'])

@router.get("/clients/get", response_model=ClientsListResponse, operation_id="get-all-clients")
async def get_all_clients(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles('admin', 'manager')),
    skip: int = Query(None, description="Number of clients to skip"),
    limit: int = Query(None, description="Number of clients to return"),
    search: str | None = Query(None, description="Search by name, email or phone"),
    related_to_me: bool | None = Query(False, description="Filter clients related to you"),
    related_to_user: str | None = Query(None, description="Filter clients related to user"),
    sort_by: str = Query("id", description="Sort by field: id, name, email, phone"),
    order: SortOrder = Query("asc", description="Sort order: asc or desc")
    ):
    logger.info('User %s requested info about all clients with attributes: ' \
                'skip=%s, limit=%s, search=%s, related_to_me=%s, related_to_user=%s, ' \
                'sort_by=%s,order=%s', 
                current_user.username, skip, limit, search, related_to_me, related_to_user, sort_by, order)
    return ClientsService.get_all(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        related_to_me=related_to_me,
        related_to_user=related_to_user,
        sort_by=sort_by,
        order=order
    )

@router.get("/clients/get/unassigned_clients", response_model=ClientsListResponse, operation_id="get-unassigned-clients")
async def get_unassigned_clients(db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    skip: int | None = Query(None, description="Number of clients to skip"),
    limit: int | None = Query(None, description="Number of clients to return"),
    search: str | None = Query(None, description="Search by name, email or phone"),
    sort_by: str = Query("id", description="Sort by field: id, name, email, phone"),
    order: SortOrder = Query("asc", description="Sort order: asc or desc")
    ):
    logger.info('User %s requested info about all unassigned clients with attributes: ' \
                'skip=%s, limit=%s, search=%s, sort_by=%s, order=%s', 
                current_user.username, skip, limit, search, sort_by, order)
    return ClientsService.get_unassigned_clients(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order
    )

@router.patch("/clients/patch/take", response_model=StatusClientsResponse, operation_id="take-unassigned-client")
async def take_unassigned_client(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user),
    client_id: int | None = Query(None, description="Search client by id"),
    name: str = Query("", description="Search client by name")
    ):
    logger.info('User %s requested take unassigned client (%s, %s)', 
                current_user.username, client_id, name) 
    return ClientsService.take_unassigned_client(
        db=db,
        current_user=current_user,
        client_id=client_id,
        name=name
    )

@router.patch("/clients/patch/delegate", response_model=StatusClientsResponse, operation_id="delegete-unassigned-client")
async def delegete_unassigned_client(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles('admin')),
    username: str = Query('User', description="Delegeted user username"),
    client_id: int | None = Query(None, description="Search client by id"),
    name: str = Query("", description="Search client by name")
    ):
    logger.info('User %s requested delegete unassigned client (%s, %s) to %s', 
                current_user.username, client_id, name, username)     
    return ClientsService.delegete_unassigned_client(
         db=db,
         username=username,
         client_id=client_id,
         name=name
    )

@router.patch("/clients/patch/discharge", response_model=StatusClientsResponse, operation_id="discharge")
async def discharge(
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_roles('admin')),
    client_id: int | None = Query(None, description="Search client by id"),
    name: str = Query("", description="Search client by name")
    ):
    logger.info('User %s requested discharge unassigned client (%s, %s)', 
                current_user.username, client_id, name)     
    return ClientsService.discharge(
         db=db,
         client_id=client_id,
         name=name
    )

@router.post("/clients/add", response_model=StatusClientsResponse, operation_id="add-client")
async def add_client(
    client: ClientCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    ):
    logger.info('User %s requested add client (%s)', 
                current_user.username, client.name)     
    return ClientsService.add_client(
         client=client,
         db=db,
         current_user=current_user
    )

@router.put("/clients/update", response_model=StatusClientsResponse, operation_id="update-client")
async def update_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin', 'manager')),
    client_id: int | None = Query(None, description="Search by id"),
    name: str = Query("", description="Search by name"),
    ):
    logger.info('User %s requested update client (%s, %s)', 
                current_user.username, client_id, name)  
    return ClientsService.update_client(
        client=client,
        db=db,
        current_user=current_user,
        client_id=client_id,
        name=name
    )

@router.delete("/clients/delete/{name}", response_model=StatusClientsResponse, operation_id="delete-client")
async def delete_client(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles('admin')),
    ):
    logger.info('User %s requested delete client (%s)', 
                current_user.username, name)  
    return ClientsService.delete_client(
        name=name,
        db=db
    )
