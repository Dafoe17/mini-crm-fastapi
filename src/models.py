from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from datetime import datetime, timezone
from src.database import Base
from src.enums import DealStatus, TaskStatus, UserRole

role_priority_map = {
    UserRole.user: 1,
    UserRole.manager: 2,
    UserRole.admin: 3,
}

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default="user")
    role_level = Column(Integer, default=0, nullable=False, index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_level = role_priority_map.get(self.role, 0)  
    
class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    notes = Column(String, nullable=True)

class Deal(Base):
    __tablename__ = 'deals'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False, unique=True, index=True)
    status = Column(Enum(DealStatus), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc), 
                        onupdate=lambda: datetime.now(timezone.utc))
    closed_at = Column(DateTime(timezone=True), nullable=True, index=True)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    title = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), 
                        default=lambda: datetime.now(timezone.utc), 
                        onupdate=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
