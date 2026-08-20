"""SAIF Auth Router — User Registration & Login"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import timedelta

from app.db.supabase_client import supabase
from app.utils.auth import hash_password, verify_password, create_access_token
from app.utils.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    organisation: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest):
    existing = supabase.table("users").select("*").eq("email", req.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(req.password)
    user_data = {
        "email": req.email,
        "password_hash": hashed,
        "full_name": req.full_name,
        "organisation": req.organisation,
        "role": "user",
        "credits": 3
    }
    result = supabase.table("users").insert(user_data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create user")

    user = result.data[0]
    token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
    logger.info(f"New user registered: {req.email}")
    return TokenResponse(access_token=token, user={"id": user["id"], "email": user["email"], "role": user["role"]})

@router.post("/login")
async def login(req: LoginRequest):
    result = supabase.table("users").select("*").eq("email", req.email).execute()
    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = result.data[0]
    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user["id"], "email": user["email"], "role": user["role"]})
    logger.info(f"User logged in: {req.email}")
    return TokenResponse(access_token=token, user={"id": user["id"], "email": user["email"], "role": user["role"], "credits": user.get("credits", 0)})
