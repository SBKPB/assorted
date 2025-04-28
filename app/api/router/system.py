from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import SessionDep
from app.core.config import settings

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health")
async def health_check(db: SessionDep):
    try:
        db.exec(select(1))  # 簡單測試資料庫可連線
        return {"status": "ok", "db_url": str(settings.SQLALCHEMY_DATABASE_URI)}
    except Exception as e:
        return {"status": "error", "details": str(e)}
