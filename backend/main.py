"""
SAIF - Smart Agentic Intelligence Framework
Creator: Md Nazmul Islam (Bijoy), NB TECH
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import traceback

from app.utils.config import get_settings
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.routers import assess, auth, payment, health, admin


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    logger.info(f"SAIF Starting - ENV={settings.ENVIRONMENT}")
    yield
    logger.info("SAIF Shutdown")


settings = get_settings()

app = FastAPI(
    title="SAIF - UK Contract Law AI",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS - Hardcoded origins for reliability
ALLOWED_ORIGINS = [
    "https://saif-smart-agentic-intelligence-uk.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time", "X-ILRMF-Engine"],
)


# Error handlers that return CORS-compatible responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        errors.append({"field": field, "message": msg})
    logger.error(f"Validation error: {errors}")
    return JSONResponse(status_code=422, content={
        "success": False,
        "error": "Validation failed",
        "details": errors,
    })


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content={
        "success": False,
        "error": exc.detail,
    })


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = f"{type(exc).__name__}: {str(exc)}"
    logger.error(f"UNHANDLED: {error_detail}")
    logger.error(traceback.format_exc())
    return JSONResponse(status_code=500, content={
        "success": False,
        "error": "Internal server error",
        "detail": error_detail,
    })


# Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start = time.time()

    if request.url.path.startswith("/api"):
        cid = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not cid:
            cid = request.client.host if request.client else "unknown"
        if rate_limiter.is_rate_limited(cid):
            return JSONResponse(status_code=429, content={"error": "Rate limited"})

    response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    response.headers["X-ILRMF-Engine"] = "v1.0"
    return response


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(assess.router, prefix="/api/v1/assess", tags=["Assessment"])
app.include_router(payment.router, prefix="/api/v1/payment", tags=["Payment"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {
        "service": "SAIF",
        "engine": "ILRMF v1.0",
        "creator": "Md Nazmul Islam (Bijoy)",
        "status": "production",
    }
