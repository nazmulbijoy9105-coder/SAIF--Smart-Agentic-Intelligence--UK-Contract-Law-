"""
SAIF Assessment Router — ILRMF Entry Point
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
    claimant: str = Field(..., min_length=2, max_length=200)
    defendant: str = Field(..., min_length=2, max_length=200)
    contractType: str = Field(default="Commercial", max_length=100)
    contractCategory: ContractCategory = Field(default=ContractCategory.B2B)
    value: Optional[float] = Field(default=None, ge=0)
    narrative: str = Field(..., min_length=20, max_length=50000)
    disputedClause: str = Field(default="", max_length=10000)
    bargainingPower: str = Field(default="equal")
    noticeAdequate: bool = Field(default=True)
    standardForm: bool = Field(default=False)
    consumerVulnerable: bool = Field(default=False)
    allowsUnilateralVariation: bool = Field(default=False)
    phase: int = Field(default=1, ge=1, le=4)

    @validator("narrative")
    def sanitize_narrative(cls, v):
        v = re.sub(r'<script[^>]*>.*?</script>', '', v, flags=re.IGNORECASE | re.DOTALL)
        return v.strip()

    @validator("bargainingPower")
    def validate_bargaining(cls, v):
        valid = ["equal", "claimant_weaker", "defendant_weaker", "significant_imbalance"]
        if v not in valid:
            raise ValueError(f"Must be one of: {valid}")
        return v


@router.post("/analyze")
async def analyze(req: AssessRequest, request: Request):
    user = await get_current_user(request)
    user_id = user["id"]

    # Credit check
    profile = await supabase_db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    if profile.get("credits_remaining", 0) <= 0:
        raise HTTPException(
            status_code=402,
            detail="No credits remaining. Upgrade at /api/v1/payment/plans",
        )

    # Run ILRMF
    try:
        result = await ilrmf_engine.assess(req.model_dump(), req.phase)
    except Exception as e:
        logger.error(f"ILRMF failed: {e}")
        raise HTTPException(status_code=502, detail="Assessment engine error")

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

    remaining = profile.get("credits_remaining", 0) - 1
    result["credits_remaining"] = remaining

    return result


@router.post("/fjr-test")
async def fjr_test(
    clause: str,
    contract_type: str = "B2B",
    bargaining_power_equal: bool = True,
    notice_adequate: bool = True,
    standard_form: bool = False,
    value: float = 10000,
):
    from app.ilrmf.fjr_engine import fjr_engine
    result = fjr_engine.assess_clause(
        clause=clause,
        contract_type=contract_type,
        bargaining_power_equal=bargaining_power_equal,
        notice_adequate=notice_adequate,
        standard_form=standard_form,
        value_of_contract=value,
    )
    return {
        "clause": clause[:200],
        "fair": result.fair,
        "just": result.just,
        "reasonable": result.reasonable,
        "score": result.score,
        "verdict": result.verdict,
        "analysis": result.analysis,
        "engine": "ILRMF v1.0 — FJR Triple-Gate",
    }


@router.get("/history")
async def get_history(request: Request, limit: int = 20, offset: int = 0):
    user = await get_current_user(request)
    history = await supabase_db.get_assessment_history(user["id"], limit, offset)
    return {"success": True, "data": history, "engine": "ILRMF v1.0"}
