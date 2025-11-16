from sqlalchemy.orm import Session
from src.models import User

class UsersRepository:

    @staticmethod
    def get_by_username(db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_by_id(db: Session, id: int) -> User | None:
        return db.query(User).filter(User.id == id).first()

    @staticmethod
    def update_password(db: Session, user: User, new_password_hash: str) -> User:
        user.password = new_password_hash
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def filter_by_role(role):
        return User.role == role
    
    @staticmethod
    def search(search: str):
        return User.username.ilike(f"%{search}%")
    
    @staticmethod
    def apply_filters(db: Session, filters: list):
        query = db.query(User)
        if filters:
            query = query.filter(*filters)
        return query.all()

    @staticmethod
    def apply_sorting(query, sort_attr, order: str):
        return query.order_by(sort_attr.desc() if order == "desc" else sort_attr.asc()).all()

    @staticmethod
    def paginate(query, skip: int | None, limit: int | None) -> list[User]:
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(query) -> int:
        return query.count()
    
    @staticmethod
    def add(db, username, password, role) -> User:
        user = User(username=username,
            password=password,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update(db, 
               db_user : User, 
               username: str,
               password: str, 
               role: str
               ) -> User:
        db_user.username = username
        db_user.password = password
        db_user.role = role
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db, user) -> User:
        db.delete(user)
        db.commit()
        return user

    @staticmethod
    def rollback(db: Session):
        db.rollback()