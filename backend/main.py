from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time, traceback
from app.utils.config import get_settings
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.routers import assess, auth, payment, health, admin

@asynccontextmanager
async def lifespan(app): yield

app = FastAPI(title="SAIF", lifespan=lifespan, docs_url="/docs" if get_settings().ENVIRONMENT != "production" else None)

@app.exception_handler(Exception)
async def exc_handler(req, exc):
    logger.error(traceback.format_exc())
    return JSONResponse(500, {"error": "Internal error"})

def _is_allowed_origin(origin: str) -> bool:
    for p in get_settings().ALLOWED_ORIGINS.split(","):
        if origin == p.strip(): return True
    return False

app.add_middleware(CORSMiddleware, allow_origins=_is_allowed_origin, allow_credentials=True, allow_methods=["*"], allow_headers=["Authorization", "Content-Type", "Stripe-Signature"])

@app.middleware("http")
async def mw(req: Request, call_next):
    start = time.time()
    if req.url.path.startswith("/api"):
        cid = req.headers.get("X-Forwarded-For", "").split(",")[0].strip() or (req.client.host if req.client else "unk")
        if rate_limiter.is_rate_limited(cid): return JSONResponse(429, {"error": "Rate limited"})
    resp = await call_next(req)
    resp.headers["X-Process-Time"] = f"{time.time()-start:.4f}s"
    resp.headers["X-ILRMF-Engine"] = "v1.0"
    resp.headers["X-SAIF-Creator"] = "Md-Nazmul-Islam-Bijoy-NB-TECH"
    return resp

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(assess.router, prefix="/api/v1/assess")
app.include_router(payment.router, prefix="/api/v1/payment")
app.include_router(admin.router, prefix="/api/v1/admin")

@app.get("/")
async def root(): return {"service": "SAIF", "engine": "ILRMF v1.0", "creator": "Md Nazmul Islam (Bijoy)", "status": "production"}
