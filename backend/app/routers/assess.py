"""
SAIF Assessment Router - Bulletproof error handling
Creator: Md Nazmul Islam (Bijoy) | NB TECH
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
import re

from app.ilrmf.engine import ilrmf_engine
from app.db.supabase_client import supabase_db
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter()


class ContractCategory(str, Enum):
    B2B = "B2B"
    B2C = "B2C"


class AssessRequest(BaseModel):
    claimant: str = Field(..., min_length=1, max_length=200)
    defendant: str = Field(..., min_length=1, max_length=200)
    contractType: str = Field(default="Commercial", max_length=100)
    contractCategory: ContractCategory = Field(default=ContractCategory.B2B)
    value: Optional[float] = Field(default=None, ge=0)
    narrative: str = Field(..., min_length=10, max_length=50000)
    disputedClause: str = Field(default="", max_length=10000)
    bargainingPower: str = Field(default="equal")
    noticeAdequate: bool = Field(default=True)
    standardForm: bool = Field(default=False)
    consumerVulnerable: bool = Field(default=False)
    allowsUnilateralVariation: bool = Field(default=False)
    phase: int = Field(default=1, ge=1, le=4)


@router.post("/analyze")
async def analyze(req: AssessRequest, request: Request):
    try:
        user = await get_current_user(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error in analyze: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_id = user.get("id", "")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Credit check
    profile = await supabase_db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    credits = profile.get("credits_remaining", 0)
    if credits <= 0:
        raise HTTPException(status_code=402, detail="No credits remaining")

    # Run ILRMF
    try:
        result = await ilrmf_engine.assess(req.model_dump(), req.phase)
    except Exception as e:
        logger.error(f"ILRMF error: {e}")
        raise HTTPException(status_code=502, detail=f"Assessment error: {str(e)}")

    if not result.get("success"):
        raise HTTPException(status_code=502, detail=result.get("error", "Unknown error"))

    # Decrement credit
    await supabase_db.decrement_credit(user_id)

    # Save
    data = result.get("data", {})
    await supabase_db.save_assessment(user_id, {
        "assessment_id": result.get("assessment_id", ""),
        "contract_type": req.contractType,
        "contract_category": req.contractCategory.value,
        "claim_value": req.value,
        "result": data,
        "phase": req.phase,
    })

    result["credits_remaining"] = credits - 1
    return result


@router.get("/history")
async def get_history(request: Request, limit: int = 20, offset: int = 0):
    try:
        user = await get_current_user(request)
        user_id = user.get("id", "")
        history = await supabase_db.get_assessment_history(user_id, limit, offset)
        return {"success": True, "data": history}
    except Exception as e:
        logger.error(f"History error: {e}")
        return {"success": True, "data": []}
