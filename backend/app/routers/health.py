from fastapi import APIRouter
from app.db.supabase_client import supabase_db
router = APIRouter()

@router.get("/health")
async def health():
    db_ok = await supabase_db.health_check()
    return {"service": "SAIF", "status": "healthy" if db_ok else "degraded", "engine": "ILRMF v1.0"}

@router.get("/health/ping")
async def ping(): return {"pong": True}
