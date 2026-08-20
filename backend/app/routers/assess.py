"""SAIF assessment API v3.1."""
from __future__ import annotations
import uuid, time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.ilrmf.engine import ilrmf_engine
from app.utils.auth import decode_token
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.db import database

router = APIRouter(prefix="/assess", tags=["ILRMF Assessment"])
security = HTTPBearer(auto_error=False)

class PaymentFacts(BaseModel):
    model_config = ConfigDict(extra="ignore")
    invoiceNumber: Optional[str] = None
    invoiceDate: Optional[str] = None
    dueDate: Optional[str] = None
    invoiceAmount: float = Field(0, ge=0)
    amountPaid: float = Field(0, ge=0)
    amountWithheld: float = Field(0, ge=0)
    withholdingReason: Optional[str] = None
    contractualWithholdingRight: Optional[bool] = None
    contractualSetOffRight: Optional[bool] = None
    statutoryWithholdingBasis: Optional[str] = None

class DefectFacts(BaseModel):
    model_config = ConfigDict(extra="ignore")
    alleged: bool = False
    defectiveUnits: int = Field(0, ge=0)
    totalUnits: int = Field(0, ge=0)
    description: Optional[str] = None
    inspectionReports: List[str] = []
    photographs: List[str] = []
    technicalEvidence: List[str] = []
    specification: Optional[str] = None
    rejectionCommunicated: Optional[bool] = None

class TerminationFacts(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clauseExists: bool = False
    noticeDate: Optional[str] = None
    noticeReceivedDate: Optional[str] = None
    curePeriodDays: Optional[int] = Field(None, ge=0)
    terminationDate: Optional[str] = None
    reservationOfRights: Optional[bool] = None
    continuedPerformanceAfterBreach: bool = False

class LossFacts(BaseModel):
    model_config = ConfigDict(extra="ignore")
    directLoss: Optional[float] = Field(None, ge=0)
    lostProfits: Optional[float] = Field(None, ge=0)
    consequentialLoss: Optional[float] = Field(None, ge=0)
    communicatedAtFormation: Optional[bool] = None

class LimitationFacts(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clauseText: Optional[str] = None
    excludesLiability: bool = False
    capsLiability: bool = False
    liabilityType: Optional[str] = None
    unusualOrOnerousTerm: bool = False

class DisputeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    claimant: str = Field(..., min_length=1, max_length=500)
    defendant: str = Field(..., min_length=1, max_length=500)
    contractType: str = Field(..., min_length=1, max_length=100)
    contractCategory: str = "B2B"
    value: float = Field(0, ge=0)
    summary: str = Field(..., min_length=10, max_length=50000)
    disputedClause: str = ""
    standardForm: bool = False
    bargainingPower: str = "equal"
    bargainingSubjectiveBelief: str = ""
    noticeObjectiveStatus: str = "adequate"
    noticeSubjectiveBelief: str = ""
    allowsUnilateralVariation: bool = False
    consumerVulnerable: bool = False
    evidenceQuality: str = "standard"
    payment: PaymentFacts = Field(default_factory=PaymentFacts)
    defect: DefectFacts = Field(default_factory=DefectFacts)
    termination: TerminationFacts = Field(default_factory=TerminationFacts)
    loss: LossFacts = Field(default_factory=LossFacts)
    limitation: LimitationFacts = Field(default_factory=LimitationFacts)
    contractualInterestRate: Optional[float] = Field(None, ge=0)
    signedDocument: Optional[bool] = True
    unusualOrOnerousTerm: bool = False
    phase: int = Field(1, ge=1, le=4)

    @field_validator("contractCategory")
    @classmethod
    def category(cls, v):
        v = v.upper().strip()
        if v not in {"B2B", "B2C"}: raise ValueError("contractCategory must be B2B or B2C")
        return v

class AssessmentResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    assessment_id: str
    phase: int

def _user_id(credentials):
    if not credentials: return "anonymous"
    try:
        payload = decode_token(credentials.credentials)
        return str(payload.get("sub", "anonymous")) if payload else "anonymous"
    except Exception: return "anonymous"

async def _run(dispute: DisputeRequest, user_id: str):
    start = time.perf_counter()
    result = await ilrmf_engine.assess(dispute.model_dump(mode="json"), phase=dispute.phase)
    logger.info("Assessment completed in %.3fs", time.perf_counter() - start)
    if not result.get("success"):
        raise HTTPException(status_code=502, detail=result.get("error", "Assessment engine failed"))
    try:
        data = result.get("data", {})
        gov = data.get("governance", {})
        relief = data.get("relief", {})
        await database.execute("""
            INSERT INTO assessments (id,user_id,assessment_id,phase,contract_type,contract_category,claim_value,overall_verdict,probability,relief,issues,governance,raw_input)
            VALUES (:id,:user_id,:assessment_id,:phase,:contract_type,:contract_category,:claim_value,:overall_verdict,:probability,:relief::jsonb,:issues::jsonb,:governance::jsonb,:raw_input::jsonb)
            RETURNING id
        """, {
            "id": str(uuid.uuid4()), "user_id": user_id if user_id != "anonymous" else None,
            "assessment_id": result.get("assessment_id"), "phase": dispute.phase,
            "contract_type": dispute.contractType, "contract_category": dispute.contractCategory,
            "claim_value": dispute.value, "overall_verdict": gov.get("overallVerdict"),
            "probability": relief.get("probability", 0), "relief": relief,
            "issues": data.get("issues", []), "governance": gov,
            "raw_input": {k:v for k,v in dispute.model_dump(mode="json").items() if k not in {"summary","disputedClause"}}
        })
    except Exception as exc:
        logger.error("Assessment persistence failed: %s", exc)
    return AssessmentResponse(**result)

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(request: Request, dispute: DisputeRequest, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    uid = _user_id(credentials)
    ip = request.client.host if request.client else "unknown"
    allowed, retry = rate_limiter.is_allowed(f"{ip}:{uid}")
    if not allowed: raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Retry after {retry}s.")
    return await _run(dispute, uid)

@router.post("/quick")
async def quick_assessment(request: Request, dispute: DisputeRequest):
    ip = request.client.host if request.client else "unknown"
    allowed, retry = rate_limiter.is_allowed(f"quick:{ip}")
    if not allowed: raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Retry after {retry}s.")
    result = await ilrmf_engine.assess(dispute.model_dump(mode="json"), phase=1)
    return result
