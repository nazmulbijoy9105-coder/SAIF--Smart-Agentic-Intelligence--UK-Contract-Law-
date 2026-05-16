from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator
import re
from app.db.supabase_client import supabase_db
router = APIRouter()

class RegisterReq(BaseModel):
    email: EmailStr; password: str = Field(..., min_length=8); full_name: str = Field(..., min_length=2)
    @validator("password")
    def pw(cls, v):
        if not re.search(r'[A-Z]', v): raise ValueError("Need uppercase")
        if not re.search(r'[0-9]', v): raise ValueError("Need number")
        return v

class LoginReq(BaseModel):
    email: EmailStr; password: str

@router.post("/register")
async def register(req: RegisterReq):
    try:
        r = await supabase_db.register(req.email, req.password, req.full_name)
        return {"success": True, "user_id": r["user"].id if r.get("user") else None, "access_token": r["session"].access_token if r.get("session") else None}
    except Exception as e: raise HTTPException(400, str(e))

@router.post("/login")
async def login(req: LoginReq):
    try:
        r = await supabase_db.login(req.email, req.password)
        if not r.get("session"): raise HTTPException(401, "Invalid credentials")
        p = await supabase_db.get_profile(r["user"].id)
        return {"success": True, "access_token": r["session"].access_token, "user_id": r["user"].id, "credits": p.get("credits_remaining", 0) if p else 0}
    except HTTPException: raise
    except: raise HTTPException(401, "Invalid credentials")

@router.get("/me")
async def me(request: Request):
    from app.utils.auth import get_current_user
    u = await get_current_user(request)
    p = await supabase_db.get_profile(u["id"])
    return {"user": u, "profile": p}
