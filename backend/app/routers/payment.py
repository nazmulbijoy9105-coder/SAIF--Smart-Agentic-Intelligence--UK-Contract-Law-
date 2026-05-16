from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
import stripe
from app.db.supabase_client import supabase_db
from app.utils.auth import get_current_user
from app.utils.config import get_settings
router = APIRouter()

class CheckoutReq(BaseModel):
    plan: str = "pro"; success_url: str; cancel_url: str

@router.post("/checkout")
async def checkout(req: CheckoutReq, request: Request):
    user = await get_current_user(request)
    s = get_settings()
    stripe.api_key = s.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.create(mode="payment", payment_method_types=["card"], line_items=[{"price_data": {"currency": "gbp", "product_data": {"name": f"SAIF {req.plan.title()}"}, "unit_amount": 1999 if req.plan=="pro" else 9999}, "quantity": 1}], success_url=req.success_url, cancel_url=req.cancel_url, client_reference_id=user["id"], metadata={"plan": req.plan})
        return {"url": session.url}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/webhook")
async def webhook(request: Request, stripe_signature: str = Header(alias="Stripe-Signature")):
    s = get_settings(); stripe.api_key = s.STRIPE_SECRET_KEY
    try:
        event = stripe.Webhook.construct_event(await request.body(), stripe_signature, s.STRIPE_WEBHOOK_SECRET)
        if event["type"] == "checkout.session.completed":
            sess = event["data"]["object"]; uid = sess.get("client_reference_id")
            if uid: await supabase_db.set_credits(uid, 50, sess.get("metadata",{}).get("plan","pro"))
        return {"received": True}
    except: raise HTTPException(400, "Invalid signature")

@router.get("/plans")
async def plans(): return {"plans": [{"id": "free", "price": "£0"}, {"id": "pro", "price": "£19.99"}, {"id": "enterprise", "price": "£99.99"}]}
