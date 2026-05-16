from fastapi import Request, HTTPException
from app.db.supabase_client import supabase_db

async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth_header.split("Bearer ")[1].strip()
    user = await supabase_db.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def require_admin(request: Request) -> dict:
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    if not profile or profile.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
