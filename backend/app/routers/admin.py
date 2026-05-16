"""
SAIF Admin Router
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter, HTTPException, Request
from app.db.supabase_client import supabase_db
from app.utils.auth import require_admin
from app.utils.logger import logger

router = APIRouter()


@router.get("/stats")
async def get_stats(request: Request):
    user = await require_admin(request)
    try:
        result = supabase_db.admin_client.table("profiles").select("id", count="exact").execute()
        total_users = result.count or 0
        result2 = supabase_db.admin_client.table("assessments").select("id", count="exact").execute()
        total_assessments = result2.count or 0
        return {
            "success": True,
            "total_users": total_users,
            "total_assessments": total_assessments,
            "engine": "ILRMF v1.0",
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Could not retrieve stats")


@router.post("/credits/add")
async def add_credits(user_id: str, amount: int, request: Request):
    await require_admin(request)
    if amount <= 0 or amount > 10000:
        raise HTTPException(status_code=400, detail="Amount must be 1-10000")
    profile = await supabase_db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    success = await supabase_db.set_credits(
        user_id, profile.get("credits_remaining", 0) + amount, profile.get("plan", "free")
    )
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add credits")
    logger.info(f"✅ Admin added {amount} credits to {user_id}")
    return {"success": True, "message": f"{amount} credits added to {user_id}"}
