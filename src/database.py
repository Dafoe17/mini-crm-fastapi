from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)

Session_local = sessionmaker(autoflush=False, 
                             autocommit=False, 
                             bind=engine)

Base = declarative_base()
