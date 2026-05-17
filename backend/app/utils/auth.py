"""
SAIF Auth Utilities
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import Request, HTTPException
from typing import Dict
from app.db.supabase_client import supabase_db
from app.utils.logger import logger


def _user_to_dict(user) -> Dict:
    """Convert any Supabase User object to a plain dict safely."""
    if user is None:
        return {}
    
    # Already a dict
    if isinstance(user, dict):
        return user
    
    # Supabase User object - extract attributes safely
    try:
        user_id = getattr(user, "id", None) or user.get("id", "")
        email = getattr(user, "email", None) or ""
        metadata = getattr(user, "user_metadata", None) or {}
        if isinstance(metadata, dict):
            full_name = metadata.get("full_name", "")
        else:
            full_name = ""
        
        return {
            "id": str(user_id) if user_id else "",
            "email": str(email) if email else "",
            "full_name": str(full_name) if full_name else "",
        }
    except Exception as e:
        logger.error(f"User conversion error: {e}")
        return {"id": "", "email": "", "full_name": ""}


async def get_current_user(request: Request) -> Dict:
    """Extract and verify user from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header.split("Bearer ")[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Empty token")

    user_obj = await supabase_db.verify_token(token)
    if not user_obj:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = _user_to_dict(user_obj)
    if not user.get("id"):
        raise HTTPException(status_code=401, detail="Invalid user data")

    return user


async def require_admin(request: Request) -> Dict:
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    if not profile or profile.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
