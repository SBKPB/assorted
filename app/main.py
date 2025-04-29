from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router

app = FastAPI()

app.include_router(api_router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory="/app/app/static"), name="static")
