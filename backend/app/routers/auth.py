"""
SAIF Auth Router - Fixed 401 errors
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field, validator
import re
from app.db.supabase_client import supabase_db
from app.utils.logger import logger

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain a number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(req: RegisterRequest, request: Request):
    try:
        result = await supabase_db.register(
            email=req.email,
            password=req.password,
            full_name=req.full_name,
        )
        user = result.get("user")
        session = result.get("session")

        if not user:
            raise HTTPException(status_code=400, detail="Registration failed")

        access_token = None
        if session:
            access_token = session.access_token

        return {
            "success": True,
            "message": "Registration successful",
            "user_id": user.id,
            "access_token": access_token,
            "engine": "ILRMF v1.0",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Email already registered")
        logger.error(f"Registration error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)


@router.post("/login")
async def login(req: LoginRequest, request: Request):
    try:
        result = await supabase_db.login(
            email=req.email,
            password=req.password,
        )
        session = result.get("session")
        user = result.get("user")

        if not session:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        profile = await supabase_db.get_profile(user.id)

        return {
            "success": True,
            "access_token": session.access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "full_name": profile.get("full_name", "") if profile else "",
            "credits_remaining": profile.get("credits_remaining", 0) if profile else 0,
            "plan": profile.get("plan", "free") if profile else "free",
            "engine": "ILRMF v1.0",
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "invalid login" in error_msg.lower() or "invalid credentials" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid email or password")
        if "email not confirmed" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Please confirm your email first. Check your inbox.")
        logger.error(f"Login error: {error_msg}")
        raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/me")
async def get_me(request: Request):
    from app.utils.auth import get_current_user
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    return {
        "success": True,
        "user": user,
        "profile": profile,
        "engine": "ILRMF v1.0",
    }
