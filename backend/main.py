"""SAIF LexQuintet ILRMF v3.1 production API."""
from __future__ import annotations
import logging, os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import assess, auth, health, payment, admin

logging.basicConfig(level=os.getenv("LOG_LEVEL","INFO"), format="%(asctime)s | %(levelname)s | %(message)s")

def cors_origins():
    return list(dict.fromkeys(x.strip().rstrip("/") for x in os.getenv("CORS_ORIGINS","").split(",") if x.strip()))

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        from app.db import database
        await database.connect()
        logging.info("Database connected")
    except Exception as exc:
        logging.error("Database connection failed; API continues: %s", exc)
    yield
    try:
        from app.db import database
        await database.disconnect()
    except Exception:
        pass

app = FastAPI(title="SAIF LexQuintet — ILRMF v3.1 API", version="3.1.0", description="AI-assisted UK contract analysis with deterministic predicates.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=cors_origins(), allow_credentials=True, allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"], allow_headers=["Authorization","Content-Type","Accept","Origin","X-Requested-With"])
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, tags=["Authentication"])
app.include_router(assess.router, tags=["ILRMF Assessment"])
app.include_router(payment.router, tags=["Payments"])
app.include_router(admin.router, tags=["Admin"])

@app.get("/", tags=["Health"])
async def root():
    return {"service":"SAIF LexQuintet","engine":"ILRMF v3.1","status":"online","api":"/docs"}
