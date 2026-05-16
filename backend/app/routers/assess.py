from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
import re
from app.ilrmf.engine import ilrmf_engine
from app.db.supabase_client import supabase_db
from app.utils.auth import get_current_user
router = APIRouter()

class Cat(str, Enum): B2B = "B2B"; B2C = "B2C"

class AssessReq(BaseModel):
    claimant: str = Field(..., min_length=2); defendant: str = Field(..., min_length=2)
    contractType: str = "Commercial"; contractCategory: Cat = Cat.B2B
    value: Optional[float] = None; narrative: str = Field(..., min_length=20)
    disputedClause: str = ""; bargainingPower: str = "equal"
    noticeAdequate: bool = True; standardForm: bool = False
    consumerVulnerable: bool = False; allowsUnilateralVariation: bool = False; phase: int = 1

@router.post("/analyze")
async def analyze(req: AssessReq, request: Request):
    user = await get_current_user(request)
    profile = await supabase_db.get_profile(user["id"])
    if not profile or profile.get("credits_remaining", 0) <= 0: raise HTTPException(402, "No credits")
    result = await ilrmf_engine.assess(req.model_dump(), req.phase)
    if not result.get("success"): raise HTTPException(502, "Engine error")
    await supabase_db.decrement_credit(user["id"])
    await supabase_db.save_assessment(user["id"], {"assessment_id": result.get("assessment_id",""), "contract_type": req.contractType, "result": result.get("data",{})})
    return result

@router.get("/history")
async def history(request: Request):
    user = await get_current_user(request)
    return {"success": True, "data": await supabase_db.get_assessment_history(user["id"])}
