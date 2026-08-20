"""SAIF Admin Router — Dashboard & Management"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any

from app.db.supabase_client import supabase
from app.utils.auth import decode_token
from app.utils.logger import logger

router = APIRouter(prefix="/admin", tags=["Admin"])
security = HTTPBearer()

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

@router.get("/stats")
async def get_stats(admin=Depends(require_admin)):
    # Aggregate assessment stats
    assessments = supabase.table("assessments").select("*").execute()
    users = supabase.table("users").select("*").execute()
    return {
        "total_assessments": len(assessments.data),
        "total_users": len(users.data),
        "recent_assessments": assessments.data[-10:] if assessments.data else []
    }

@router.get("/users")
async def list_users(admin=Depends(require_admin)):
    result = supabase.table("users").select("id, email, full_name, role, credits, created_at").execute()
    return result.data

@router.post("/users/{user_id}/credits")
async def add_credits(user_id: str, amount: int, admin=Depends(require_admin)):
    user = supabase.table("users").select("credits").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")
    new_credits = user.data[0]["credits"] + amount
    supabase.table("users").update({"credits": new_credits}).eq("id", user_id).execute()
    logger.info(f"Admin added {amount} credits to user {user_id}")
    return {"user_id": user_id, "new_credits": new_credits}
