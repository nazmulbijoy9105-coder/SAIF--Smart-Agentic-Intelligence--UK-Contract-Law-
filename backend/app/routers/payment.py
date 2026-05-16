"""
SAIF Payment Router — Stripe UK
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel, Field
import stripe

from app.db.supabase_client import supabase_db
from app.utils.auth import get_current_user
from app.utils.config import get_settings
from app.utils.logger import logger

router = APIRouter()

PLANS = {
    "pro": {"name": "SAIF Pro", "credits": 50, "amount_pence": 1999},
    "enterprise": {"name": "SAIF Enterprise", "credits": 999, "amount_pence": 9999},
}


class CheckoutRequest(BaseModel):
    plan: str = "pro"
    success_url: str = Field(..., max_length=500)
    cancel_url: str = Field(..., max_length=500)


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest, request: Request):
    user = await get_current_user(request)
    user_id = user["id"]
    settings = get_settings()

    plan_config = PLANS.get(req.plan)
    if not plan_config:
        raise HTTPException(status_code=400, detail="Invalid plan")

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": settings.STRIPE_CURRENCY,
                    "product_data": {
                        "name": plan_config["name"],
                        "description": f"{plan_config['credits']} assessments — ILRMF Engine",
                    },
                    "unit_amount": plan_config["amount_pence"],
                },
                "quantity": 1,
            }],
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            client_reference_id=user_id,
            metadata={
                "user_id": user_id,
                "plan": req.plan,
                "credits": plan_config["credits"],
            },
        )
        return {"success": True, "url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail="Checkout creation failed")


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="Stripe-Signature"),
):
    settings = get_settings()
    payload = await request.body()

    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        logger.error(f"Webhook verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type", "")
    logger.info(f"Stripe webhook: {event_type}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session.get("client_reference_id")
        metadata = session.get("metadata", {})
        credits = int(metadata.get("credits", 0))
        plan = metadata.get("plan", "pro")

        if user_id and credits > 0:
            profile = await supabase_db.get_profile(user_id)
            current = profile.get("credits_remaining", 0) if profile else 0
            await supabase_db.set_credits(user_id, current + credits, plan)
            logger.info(f"✅ Credits added: user={user_id} +{credits}")

    return {"received": True}


@router.get("/credits")
async def get_credits(request: Request):
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    return {
        "success": True,
        "credits_remaining": profile.get("credits_remaining", 0) if profile else 0,
        "plan": profile.get("plan", "free") if profile else "free",
    }


@router.get("/plans")
async def get_plans():
    return {
        "plans": [
            {"id": "free", "name": "SAIF Free", "credits": 3, "price": "£0"},
            {"id": "pro", "name": "SAIF Pro", "credits": 50, "price": "£19.99"},
            {"id": "enterprise", "name": "SAIF Enterprise", "credits": 999, "price": "£99.99"},
        ],
        "engine": "ILRMF v1.0",
    }
