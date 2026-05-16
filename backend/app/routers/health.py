"""
SAIF Health Router
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter
from app.db.supabase_client import supabase_db
from app.utils.logger import logger

router = APIRouter()


@router.get("/health")
async def health_check():
    """Full dependency health check."""
    checks = {}

    # Supabase
    try:
        checks["supabase"] = await supabase_db.health_check()
    except Exception:
        checks["supabase"] = False

    # Gemini
    try:
        from app.utils.config import get_settings
        checks["gemini"] = bool(get_settings().GEMINI_API_KEY)
    except Exception:
        checks["gemini"] = False

    all_ok = all(checks.values())

    return {
        "service": "SAIF — UK Contract Law AI",
        "status": "healthy" if all_ok else "degraded",
        "engine": "ILRMF v1.0",
        "creator": "Md Nazmul Islam (Bijoy) — NB TECH",
        "dependencies": checks,
    }


@router.get("/health/ping")
async def ping():
    return {"pong": True, "engine": "ILRMF v1.0"}
