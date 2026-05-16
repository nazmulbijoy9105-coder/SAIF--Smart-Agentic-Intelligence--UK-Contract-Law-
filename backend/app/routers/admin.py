from fastapi import APIRouter, HTTPException
from app.db.supabase_client import supabase_db
from app.utils.auth import require_admin
router = APIRouter()

@router.get("/stats")
async def stats(request: Request):
    await require_admin(request)
    u = supabase_db.admin_client.table("profiles").select("id", count="exact").execute()
    a = supabase_db.admin_client.table("assessments").select("id", count="exact").execute()
    return {"users": u.count, "assessments": a.count}

@router.post("/credits/add")
async def add_credits(user_id: str, amount: int, request: Request):
    await require_admin(request)
    p = await supabase_db.get_profile(user_id)
    if not p: raise HTTPException(404, "Not found")
    await supabase_db.set_credits(user_id, p.get("credits_remaining",0)+amount, p.get("plan","free"))
    return {"success": True}
