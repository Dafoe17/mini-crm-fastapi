from src.core.logger import logger
from fastapi import APIRouter

from src.api.users import router as users_router
from src.api.clients import router as clients_router
from src.api.deals import router as deals_router
from src.api.tasks import router as tasks_router
from src.api.auth import router as auth_router

from src.database import Base, engine

main_router = APIRouter()

logger.debug('Include auth router')
main_router.include_router(auth_router)
logger.debug('Include users router')
main_router.include_router(users_router)
logger.debug('Include clients router')
main_router.include_router(clients_router)
logger.debug('Include deals router')
main_router.include_router(deals_router)
logger.debug('Include tasks router')
main_router.include_router(tasks_router)

Base.metadata.create_all(bind=engine)
