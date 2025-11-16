from sqlalchemy import asc, desc
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
    def base_query(db: Session):
        return db.query(Client)
    
    @staticmethod
    def get_unassign(db: Session):
        return db.query(Client).filter(Client.user_id == None)
    
    @staticmethod
    def filter_related_to_user(query, username):
        user_ids = query(Client.id).filter(Client.username.ilike(f"%{username}%"))
        query = query.filter(Client.user_id.in_(user_ids))
        return query

    @staticmethod
    def filter_related_to_me(query, current_user):
        query = query.filter(Client.user_id == current_user.id)
        return query

    @staticmethod
    def search(query, search: str):
        query = query.filter(
        (Client.name.ilike(f"%{search}%")) |
        (Client.email.ilike(f"%{search}%")) |
        (Client.phone.ilike(f"%{search}%")))
        return query

    @staticmethod
    def apply_sorting(query, sort_attr, order: str):
        query = query.order_by(sort_attr.desc() if order == "desc" else sort_attr.asc())
        return query

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

        db_client = Client(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone,
            notes=notes)

        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    
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