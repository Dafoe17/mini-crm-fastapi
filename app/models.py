from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from database import Base
from enums import DealStatus, TaskStatus


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, index=True)
    password_hash = Column(String)
    

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    phone = Column(String, index=True)
    notes = Column(String)

class Deal(Base):
    __tablename__ = 'deals'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), index=True)
    title = Column(String, nullable=False, index=True)
    status = Column(Enum(DealStatus, name='deal_status'), nullable=False, index=True)
    value = Column(Integer)
    created_at = Column(DateTime, index=True)
    closed_at = Column(DateTime, index=True)

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus, name='task_status'), nullable=False, index=True)
    due_date = Column(DateTime, index=True)

    deal = relationship('Deal')