"""
SAIF — Smart Agentic Intelligence Framework
UK Contract Law AI — Production Build
Creator: Md Nazmul Islam (Bijoy), Advocate Supreme Court of Bangladesh
Founder & Chairman, NB TECH | ILRMF Engine
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import traceback

from app.utils.config import get_settings
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.routers import assess, auth, payment, health, admin


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    logger.info("=" * 60)
    logger.info(f"🚀 SAIF Starting — ENV={settings.ENVIRONMENT}")
    logger.info(f"   Engine: ILRMF v1.0")
    logger.info(f"   Creator: Md Nazmul Islam (Bijoy) — NB TECH")
    logger.info(f"   Allowed Origins: {settings.allowed_origins_list}")
    logger.info("=" * 60)
    yield
    logger.info("🛑 SAIF Shutdown — ILRMF Engine stopped")


settings = get_settings()

app = FastAPI(
    title="SAIF — UK Contract Law AI",
    description="ILRMF Engine by Md Nazmul Islam (Bijoy) / NB TECH",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)


# ── Global Exception Handler ────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"UNHANDLED: {type(exc).__name__}: {exc}\n{traceback.format_exc()}")
    return JSONResponse(status_code=500, content={
        "success": False,
        "error": "Internal server error",
        "detail": "An unexpected error occurred.",
        "engine": "ILRMF v1.0",
    })


# ── CORS — FIXED: List-based origins ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)


# ── Rate Limit + Security Headers Middleware ──────────────────
@app.middleware("http")
async def middleware_stack(request: Request, call_next):
    start = time.time()

    # Rate limit
    if request.url.path.startswith("/api"):
        client_id = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_id:
            client_id = request.client.host if request.client else "unknown"
        if rate_limiter.is_rate_limited(client_id):
            return JSONResponse(status_code=429, content={
                "error": "Rate limit exceeded",
                "retry_after": "60 seconds",
                "engine": "ILRMF v1.0",
            })

    response = await call_next(request)
    elapsed = time.time() - start

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-SAIF-Creator"] = "Md-Nazmul-Islam-Bijoy-NB-TECH"
    response.headers["X-ILRMF-Engine"] = "v1.0"
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"

    return response


# ── Routers ──────────────────────────────────────────────────
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(assess.router, prefix="/api/v1/assess", tags=["Assessment"])
app.include_router(payment.router, prefix="/api/v1/payment", tags=["Payment"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {
        "service": "SAIF — Smart Agentic Intelligence Framework",
        "engine": "ILRMF v1.0",
        "creator": "Md Nazmul Islam (Bijoy)",
        "org": "NB TECH Bangladesh",
        "jurisdiction": "UK Contract Law",
        "governance": "Fair · Just · Reasonable",
        "hallucination": "ZERO tolerance",
        "status": "production",
    }
