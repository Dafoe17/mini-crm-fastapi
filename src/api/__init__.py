from fastapi import APIRouter

from src.api.users import router as users_router
from src.api.clients import router as clients_router
from src.api.deals import router as deals_router
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router

from src.database import Base, engine

main_router = APIRouter()

main_router.include_router(users_router)
main_router.include_router(clients_router)
main_router.include_router(deals_router)
main_router.include_router(tasks_router)
main_router.include_router(auth_router)

Base.metadata.create_all(bind=engine)
