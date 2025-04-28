from fastapi import APIRouter

from app.api.router import albums, system

api_router = APIRouter()

api_router.include_router(system.router)
api_router.include_router(albums.router)
