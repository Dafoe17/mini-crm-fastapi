from sqlalchemy import _or 
from sqlalchemy.orm import Session
from src.models import Client

class ClientsRepository:
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Client | None:
        return db.query(Client).filter(Client.name == name).first()
    
    @staticmethod
    def get_by_id(db: Session, id: int) -> Client | None:
        return db.query(Client).filter(Client.id == id).first()
    
    @staticmethod
    def get_unassign():
        return Client.user_id == None
    
    @staticmethod
    def filter_related_to_user(db: Session, username: str):
        user_ids = db.query(Client.id).filter(Client.username.ilike(f"%{username}%"))
        Client.user_id.in_(user_ids)
        return Client.user_id.in_(user_ids)

    @staticmethod
    def search(search: str):
        return _or(
            Client.name.ilike(f"%{search}%"),
            Client.email.ilike(f"%{search}%"),
            Client.phone.ilike(f"%{search}%")
            )
    
    @staticmethod
    def apply_filters(db: Session, filters: list):
        query = db.query(Client)
        if filters:
            query = query.filter(*filters)
        return query.all()

    @staticmethod
    def apply_sorting(query, sort_attr, order: str):
        return query.order_by(sort_attr.desc() if order == "desc" else sort_attr.asc()).all()

    @staticmethod
    def paginate(query, skip: int | None, limit: int | None) -> list[Client]:
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(query) -> int:
        return query.count()
    
    @staticmethod
    def take_client(db: Session, client, id: int | None) -> int:
        client.user_id = id
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def add(db, 
            user_id,
            name,
            email,
            phone,
            notes) -> Client:

        client = Client(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            notes=notes)

        db.add(client)
        db.commit()
        db.refresh(client)
        return client
    
    @staticmethod
    def update(db, 
               client,
               user_id,
               name,
               email,
               phone,
               notes
               ) -> Client:
        
        client.user_id = user_id
        client.name = name
        client.email = email
        client.phone = phone
        client.notes = notes
        db.commit()
        db.refresh(client)
        return client

    @staticmethod
    def delete(db, client) -> Client:
        db.delete(client)
        db.commit()
        return client

    @staticmethod
    def rollback(db: Session):
        db.rollback()