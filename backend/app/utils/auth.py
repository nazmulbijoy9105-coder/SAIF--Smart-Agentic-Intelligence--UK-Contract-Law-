"""
SAIF Auth Utilities — JWT verification
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import Request, HTTPException
from typing import Optional, Dict
from app.db.supabase_client import supabase_db
from app.utils.logger import logger


async def get_current_user(request: Request) -> Dict:
    """Extract and verify user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
        )

    token = auth_header.split("Bearer ")[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")

    user = await supabase_db.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    return user


async def require_admin(request: Request) -> Dict:
    """Verify user is admin."""
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])

    if not profile or profile.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return user
