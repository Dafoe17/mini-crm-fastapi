from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from src.api import main_router

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    msg = exc.errors()[0]["msg"]
    raise HTTPException(status_code=400, detail=msg)

app.include_router(main_router)
