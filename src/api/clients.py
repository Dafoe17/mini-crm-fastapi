from fastapi import APIRouter, HTTPException, Query, Depends, Path
from src.api.dependencies import Session, get_db, get_current_user, require_roles

from src.enums import SortOrder
from src.models import User, Client
from src.schemas.client import ClientRead, ClientCreate, ClientsListResponse, StatusClientsResponse


router = APIRouter(tags=['Clients'])

@router.get("/clients/get", response_model=ClientsListResponse, operation_id="get-all-clients")
async def get_all_clients(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    skip: int = Query(None, description="Number of users to skip"),
                    limit: int = Query(None, description="Number of users to return"),
                    search: str | None = Query(None, description="Search by name, email or phone"),
                    related_to_user: str | None = Query(None, description="Filter clients related to user"),
                    sort_by: str = Query("id", description="Sort by field: id, name, email, phone"),
                    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                    ) -> ClientsListResponse:
    
    query = db.query(Client)

    if related_to_user:
        user_ids = db.query(User.id).filter(User.username.ilike(f"%{related_to_user}%")).subquery()
        query = query.filter(Client.user_id.in_(user_ids))
    
    if search:
        query = query.filter(
        (Client.name.ilike(f"%{search}%")) |
        (Client.email.ilike(f"%{search}%")) |
        (Client.phone.ilike(f"%{search}%")))

    if hasattr(Client, sort_by):
        sort_attr = getattr(Client, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_clients = query.count()
    clients = query.offset(skip).limit(limit).all()

    return ClientsListResponse(
        total=total_clients,
        skip=skip,
        limit=limit,
        clients=[ClientRead.model_validate(client) for client in clients]
    )

@router.get("/clients/get/my", response_model=ClientsListResponse, operation_id="get-my-clients")
async def get_my_clients(db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user),
                    skip: int | None = Query(None, description="Number of users to skip"),
                    limit: int | None = Query(None, description="Number of users to return"),
                    search: str | None = Query(None, description="Search by name, email or phone"),
                    sort_by: str = Query("id", description="Sort by field: id, name, email, phone"),
                    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                    ) -> ClientsListResponse:
    
    query = db.query(Client).filter(Client.user_id == current_user.id)

    if search:
        query = query.filter(
        (Client.name.ilike(f"%{search}%")) |
        (Client.email.ilike(f"%{search}%")) |
        (Client.phone.ilike(f"%{search}%")))

    if hasattr(Client, sort_by):
        sort_attr = getattr(Client, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_clients = query.count()
    clients = query.offset(skip).limit(limit).all()

    return ClientsListResponse(
        total=total_clients,
        skip=skip,
        limit=limit,
        clients=[ClientRead.model_validate(client) for client in clients]
    )

@router.get("/clients/get/unassigned_clients", response_model=ClientsListResponse, operation_id="get-unassigned-clients")
async def get_unassigned_clients(db: Session = Depends(get_db), 
                    _: User = Depends(get_current_user),
                    skip: int | None = Query(None, description="Number of users to skip"),
                    limit: int | None = Query(None, description="Number of users to return"),
                    search: str | None = Query(None, description="Search by name, email or phone"),
                    sort_by: str = Query("id", description="Sort by field: id, name, email, phone"),
                    order: SortOrder = Query("asc", description="Sort order: asc or desc"),
                    ) -> ClientsListResponse:
    
    query = db.query(Client).filter(Client.user_id == None)
    
    if search:
        query = query.filter(
        (Client.name.ilike(f"%{search}%")) |
        (Client.email.ilike(f"%{search}%")) |
        (Client.phone.ilike(f"%{search}%")))

    if hasattr(Client, sort_by):
        sort_attr = getattr(Client, sort_by)
        query = query.order_by(sort_attr.desc() if order.lower() == "desc" else sort_attr.asc())
    else:
        raise HTTPException(status_code=400, detail=f"Invalid sort field: {sort_by}")

    total_clients = query.count()
    clients = query.offset(skip).limit(limit).all()

    return ClientsListResponse(
        total=total_clients,
        skip=skip,
        limit=limit,
        clients=[ClientRead.model_validate(client) for client in clients]
    )

@router.patch("/clients/patch/take_client", response_model=StatusClientsResponse, operation_id="take-unassigned-client")
async def take_unassigned_clients(db: Session = Depends(get_db), 
                    current_user: User = Depends(get_current_user),
                    client_id: int | None = Query(None, description="Search client by id"),
                    name: str = Query('Client', description="Search client by name"),
                    ) -> StatusClientsResponse:
    
    if client_id:
        db_client = db.query(Client).filter(Client.id == client_id).first()
    else:
        db_client = db.query(Client).filter((Client.name.ilike(f"%{name}%"))).first()

    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if db_client.user_id:
        raise HTTPException(status_code=400, detail=f"Client {db_client.name} is already assigned.")

    db_client.user_id = current_user.id
    
    try:
        db.commit()
        db.refresh(db_client)
        response = StatusClientsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to take client: {str(e)}"
        )

    response.clients = ClientRead.model_validate(db_client)

    return response

@router.patch("/clients/patch/delegate_client", response_model=StatusClientsResponse, operation_id="delegete-unassigned-client")
async def delegete_unassigned_clients(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    username: str = Query('User', description="Search user by name"),
                    client_id: int | None = Query(None, description="Search client by id"),
                    name: str = Query("", description="Search client by name"),
                    ) -> StatusClientsResponse:
    
    if client_id:
        db_client = db.query(Client).filter(Client.id == client_id).first()
    else:
        db_client = db.query(Client).filter((Client.name.ilike(f"%{name}%"))).first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    assigned_user = db.query(User).filter(User.username == username).first()
    if not assigned_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_client.user_id = assigned_user.id
    
    try:
        db.commit()
        db.refresh(db_client)
        response = StatusClientsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to delegete client: {str(e)}"
        )

    response.clients = ClientRead.model_validate(db_client)

    return response

@router.patch("/clients/patch/discharge", response_model=StatusClientsResponse, operation_id="discharge")
async def discharge(db: Session = Depends(get_db), 
                    _: User = Depends(require_roles('admin', 'manager')),
                    client_id: int | None = Query(None, description="Search client by id"),
                    name: str = Query("", description="Search client by name"),
                    ) -> StatusClientsResponse:
    
    if client_id:
        db_client = db.query(Client).filter(Client.id == client_id).first()
    else:
        db_client = db.query(Client).filter((Client.name.ilike(f"%{name}%"))).first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_client.user_id = None
    
    try:
        db.commit()
        db.refresh(db_client)
        response = StatusClientsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to discharge user from client: {str(e)}"
        )

    response.clients = ClientRead.model_validate(db_client)

    return response

@router.post("/clients/add", response_model=StatusClientsResponse, operation_id="add-client")
async def create_client(client: ClientCreate, 
                        db: Session = Depends(get_db),
                        current_user: User = Depends(require_roles('admin', 'manager')),
                        ) -> StatusClientsResponse:
    query = db.query(Client).filter(Client.name == client.name).first()
    if query:
        raise HTTPException(status_code=404, detail="Client already exists")
    
    if current_user.role == 'manager':
        user_id = current_user.id

    else:
        assigned_user = db.query(User).filter(User.username == client.user_name).first()
        if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = assigned_user.id

    db_client = Client(user_id=user_id,
                       name=client.name,
                       email=client.email,
                       phone=client.phone,
                       notes=client.notes)
    try:
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        response = StatusClientsResponse(
            status="created",
        )

    except Exception as e:
        db.rollback() 
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to create user: {str(e)}"
        )
    
    response.clients = ClientRead.model_validate(db_client)

    return response

@router.put("/clients/update", response_model=StatusClientsResponse, operation_id="update-client")
async def update_client(client: ClientCreate,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(require_roles('admin', 'manager')),
                        client_id: int | None = Query(None, description="Search by id"),
                        name: str = Query("", description="Search by name"),
                        ) -> StatusClientsResponse:
    
    if client_id:
        db_client = db.query(Client).filter(Client.id == client_id).first()
    else:
        db_client = db.query(Client).filter((Client.name.ilike(f"%{name}%"))).first()

    if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    assigned_user = db.query(User).filter(User.username == client.user_name).first()
    if not assigned_user:
            raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.role == 'manager':
        if assigned_user.id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail=f""""Access denied. 
                Your role able to update only clients related to your user"""
            )
    
    db_client.user_id = assigned_user.id
    db_client.name = client.name
    db_client.email = client.email
    db_client.phone = client.phone
    db_client.notes = client.notes

    try:
        db.commit()
        db.refresh(db_client)
        response = StatusClientsResponse(
            status="changed"
        )
    except Exception as e:
        db.rollback()
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to change client: {str(e)}"
        )

    response.clients = ClientRead.model_validate(db_client)

    return response

@router.delete("/clients/delete/", response_model=StatusClientsResponse, operation_id="delete-client")
async def delete_client(name: str = Query("", description="Delete by name"),
                        db: Session = Depends(get_db),
                        _: User = Depends(require_roles('admin')),
                        ) -> StatusClientsResponse:

    db_client = db.query(Client).filter((Client.name.ilike(f"%{name}%"))).first()

    if not db_client:
            raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        db.delete(db_client)
        db.commit()
        response = StatusClientsResponse(
            status="deleted",
        )
    except Exception as e:
        db.rollback()
        response = StatusClientsResponse(
            status="error",
            details=f"Failed to delete client: {str(e)}"
        )

    response.clients = ClientRead.model_validate(db_client)

    return response
