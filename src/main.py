from src.core.logger import logger
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from src.api import main_router

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    msg = exc.errors()[0]["msg"]
    raise HTTPException(status_code=400, detail=msg)

app.include_router(main_router)

if __name__ == "__main__":
    logger.info('Initializing the application')
    uvicorn.run("src.main:app", host="0.0.0.0", log_config="src/core/log_config.yaml")
