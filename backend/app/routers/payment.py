"""SAIF Payment Router — Credit Top-ups (Stripe Integration Stub)
In production, integrate Stripe/PayPal here and update user credits on webhook.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.db.supabase_client import supabase
from app.utils.auth import decode_token
from app.utils.logger import logger

router = APIRouter(prefix="/payment", tags=["Payments"])

class CreditTopUpRequest(BaseModel):
    package: str  # basic, standard, premium
    payment_method: Optional[str] = "stripe"

CREDIT_PACKAGES = {
    "basic": {"credits": 5, "price_gbp": 9.99},
    "standard": {"credits": 15, "price_gbp": 24.99},
    "premium": {"credits": 50, "price_gbp": 49.99},
}

@router.post("/topup")
async def topup_credits(
    req: CreditTopUpRequest,
    token: str = Depends(lambda x: x.headers.get("Authorization", "").replace("Bearer ", ""))
):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if req.package not in CREDIT_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    pkg = CREDIT_PACKAGES[req.package]
    user_id = payload["sub"]

    # TODO: Integrate Stripe Checkout Session here
    # For now, simulate success
    user = supabase.table("users").select("credits").eq("id", user_id).execute()
    if not user.data:
        raise HTTPException(status_code=404, detail="User not found")

    new_credits = user.data[0]["credits"] + pkg["credits"]
    supabase.table("users").update({"credits": new_credits}).eq("id", user_id).execute()

    logger.info(f"Payment: {req.package} for user {user_id}")
    return {
        "success": True,
        "package": req.package,
        "credits_added": pkg["credits"],
        "new_balance": new_credits,
        "amount_gbp": pkg["price_gbp"]
    }

@router.get("/packages")
async def list_packages():
    return CREDIT_PACKAGES
