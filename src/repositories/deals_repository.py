from sqlalchemy.orm import Session
from src.models import User, Client, Deal
from datetime import datetime, timedelta

class DealsRepository:
    
    @staticmethod
    def get_by_id(db: Session, id: int):
        return db.query(Deal).filter(Deal.id == id).first()
    
    @staticmethod
    def get_by_title(db: Session, title: str):
        return db.query(Deal).filter(Deal.title == title).first()
    
    @staticmethod
    def get_by_client_name(db: Session, name: str):
        client_ids = db.query(Client.id).filter(Client.name.islike(f"%{name}%")).subquery()
        return Deal.client_id.in_(client_ids)
    
    @staticmethod
    def get_by_username(db: Session, username: str):
        user_ids = db.query(User.id).filter(User.username.islike(f"%{username}%")).subquery
        client_ids = db.query(Client.id).filter(Client.user_id.in_(user_ids))
        return Deal.client_id.in_(client_ids)
    
    @staticmethod
    def search(search: str):
        return Deal.title.ilike(f"%{search}%")
    
    @staticmethod
    def more_than(value: int):
        return Deal.value >= value
    
    @staticmethod
    def less_than(value: int):
        return Deal.value >= value
    
    @staticmethod
    def exact_date(date: datetime, attribute: str):
        start_of_day = datetime.combine(date.date(), datetime.min.time())
        end_of_day = datetime.combine(date.date(), datetime.max.time())
        col = getattr(Deal, attribute)
        return col >= start_of_day, col <= end_of_day
    
    @staticmethod
    def earlier_than(date: datetime, attribute: str):
        return getattr(Deal, attribute) <= date
    
    @staticmethod
    def later_than(date: datetime, attribute: str):
        return getattr(Deal, attribute) >= date
    
    @staticmethod
    def new(attribute: str):
        today = datetime.today()
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        end_of_month = next_month - timedelta(seconds=1)

        col = getattr(Deal, attribute)
        return col >= start_of_month, col <= end_of_month
    
    @staticmethod
    def apply_filters(db: Session, filters: list):
        query = db.query(Deal)
        if filters:
            query = query.filter(*filters)
        return query.all()

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
    def add(db : Session, 
            client_id : int,
            title : str,
            status : str,
            value : int,
            closed_at : datetime) -> Deal:

        deal = Deal(client_id=client_id,
                       title=title,
                       status=status,
                       value=value,
                       closed_at=closed_at)

        db.add(deal)
        db.commit()
        db.refresh(deal)
        return deal
    
    @staticmethod
    def update(db : Session, 
               deal : Deal,
               client_id : int,
               tittle : str,
               status : str,
               value : int,
               closed_at : datetime
               ) -> Deal:
        
        deal.client_id = client_id
        deal.tittle = tittle
        deal.status = status
        deal.value = value
        deal.closed_at = closed_at
        db.commit()
        db.refresh(deal)
        return deal

    @staticmethod
    def delete(db: Session, deal) -> Deal:
        db.delete(deal)
        db.commit()
        return deal
    
    @staticmethod
    def delete_all_by_client(db: Session, client_id: int) -> list:
        deals = db.query(Deal).filter((Deal.client_id == client_id)).all()
        deals.delete(synchronize_session='fetch')
        db.commit()
        return deals

    @staticmethod
    def rollback(db: Session):
        db.rollback()