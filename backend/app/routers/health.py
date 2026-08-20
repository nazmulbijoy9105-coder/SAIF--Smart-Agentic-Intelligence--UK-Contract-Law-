"""SAIF Health Check Router"""
from fastapi import APIRouter
from app.ilrmf.engine import ilrmf_engine
from app.utils.config import get_settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "engine": "ILRMF v3.0",
        "ai_provider": settings.AI_PROVIDER,
        "groq_available": ilrmf_engine.groq_client is not None
    }
