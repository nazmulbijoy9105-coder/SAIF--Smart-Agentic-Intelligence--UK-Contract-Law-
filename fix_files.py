import os

# Fix engine.py
engine_code = r'''"""
SAIF ILRMF Core Engine
Creator: Md Nazmul Islam (Bijoy) | NB TECH | ILRMF
"""
import json
import re
import uuid
import time
import google.generativeai as genai
from app.ilrmf.fjr_engine import fjr_engine
from app.validators.citation_checker import citation_checker
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES
from app.utils.config import get_settings
from app.utils.logger import logger

settings = get_settings()
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "YOU ARE SAIF - UK Contract Law AI powered by ILRMF. "
    "Creator: Md Nazmul Islam (Bijoy), NB TECH. "
    "VERIFIED CASES: {cases} "
    "VERIFIED STATUTES: {statutes} "
    "FJR TRIPLE-GATE ON EVERY CLAUSE. ZERO HALLUCINATION. "
    "Return ONLY valid JSON with keys: facts, issues, relief, governance. "
    "Each issue must have: issue, law, fjr(fair,just,reasonable,score,analysis), "
    "argument(claimant,defendant), verdict. "
    "Governance must include: hallucination=ZERO, engine=ILRMF v1.0."
)


class ILRMFEngine:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if not self._model:
            self._model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config=genai.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                ),
            )
        return self._model

    async def assess(self, dispute: dict, phase: int = 1) -> dict:
        phase = max(1, min(phase, 4))
        aid = f"ILRMF-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"ILRMF Assessment: {aid} | Phase={phase}")

        raw_result = await self._call_gemini(dispute, phase)
        if not raw_result.get("success"):
            return raw_result

        parsed = raw_result["data"]

        for issue in parsed.get("issues", []):
            clause = dispute.get("disputedClause", "") or issue.get("issue", "")
            try:
                fjr = fjr_engine.assess_clause(
                    clause=clause,
                    contract_type=dispute.get("contractCategory", "B2B"),
                    bargaining_power_equal=dispute.get("bargainingPower") == "equal",
                    notice_adequate=dispute.get("noticeAdequate", True),
                    standard_form=dispute.get("standardForm", False),
                    value_of_contract=float(dispute.get("value") or 0),
                    allows_unilateral_variation=dispute.get("allowsUnilateralVariation", False),
                    consumer_vulnerable=dispute.get("consumerVulnerable", False),
                )
                issue["fjr"] = {
                    "fair": fjr.fair,
                    "just": fjr.just,
                    "reasonable": fjr.reasonable,
                    "score": fjr.score,
                    "analysis": fjr.analysis,
                    "fairScore": fjr.fair_score,
                    "justScore": fjr.just_score,
                    "reasonableScore": fjr.reasonable_score,
                }
                if not fjr.fair or not fjr.just or not fjr.reasonable:
                    issue["verdict"] = fjr.verdict
            except Exception as e:
                logger.warning(f"FJR error: {e}")

        validation = citation_checker.validate(parsed, phase)
        hallucination = "ZERO" if validation["passed"] else "FLAGGED"

        parsed.setdefault("governance", {})
        parsed["governance"]["citationValidation"] = validation
        parsed["governance"]["hallucination"] = hallucination
        parsed["governance"]["assessmentId"] = aid
        parsed["governance"]["engine"] = "ILRMF v1.0"
        parsed["governance"]["creator"] = "Md Nazmul Islam (Bijoy)"
        parsed["governance"]["org"] = "NB TECH Bangladesh"
        parsed["governance"]["phase"] = phase

        claim_value = float(dispute.get("value") or 0)
        if claim_value <= 10000:
            court = "Small Claims Track"
        elif claim_value <= 25000:
            court = "Fast Track (County Court)"
        elif claim_value <= 100000:
            court = "Multi Track (County Court)"
        else:
            court = "High Court (Kings Bench Division)"
        parsed["governance"]["courtTrack"] = court

        logger.info(f"ILRMF Complete: {aid} | Hallucination={hallucination}")

        return {
            "success": True,
            "data": parsed,
            "assessment_id": aid,
            "phase": phase,
        }

    async def _call_gemini(self, dispute: dict, phase: int) -> dict:
        cases_str = ", ".join([f"{c.name} {c.citation}" for c in PHASE1_CASES])
        stat_str = ", ".join([f"{s.act} {s.section}" for s in STATUTES])
        prompt = SYSTEM_PROMPT.format(cases=cases_str, statutes=stat_str)
        prompt += "\n\nDISPUTE: " + json.dumps(dispute, default=str)

        for attempt in range(3):
            try:
                resp = self.model.generate_content(prompt)
                raw = resp.text.strip()
                if not raw:
                    raise ValueError("Empty response")
                parsed = self._parse_json(raw)
                logger.info(f"Gemini OK: attempt={attempt+1} chars={len(raw)}")
                return {"success": True, "data": parsed}
            except json.JSONDecodeError as e:
                logger.warning(f"JSON error (attempt {attempt+1}): {e}")
            except Exception as e:
                logger.warning(f"Gemini error (attempt {attempt+1}): {e}")
            if attempt < 2:
                time.sleep(2 * (attempt + 1))

        return {"success": False, "error": "Gemini failed after 3 attempts"}

    def _parse_json(self, raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            return {
                "facts": {"parse_error": True},
                "issues": [],
                "relief": {},
                "governance": {"hallucination": "PARSE_ERROR"},
            }


ilrmf_engine = ILRMFEngine()
'''

with open('backend/app/ilrmf/engine.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(engine_code)
print("OK: engine.py")


# Fix main.py
main_code = r'''"""
SAIF - Smart Agentic Intelligence Framework
Creator: Md Nazmul Islam (Bijoy), NB TECH
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
import traceback

from app.utils.config import get_settings
from app.utils.logger import logger
from app.utils.rate_limiter import rate_limiter
from app.routers import assess, auth, payment, health, admin


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings = get_settings()
    logger.info(f"SAIF Starting - ENV={settings.ENVIRONMENT}")
    yield
    logger.info("SAIF Shutdown")


settings = get_settings()

app = FastAPI(
    title="SAIF - UK Contract Law AI",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"UNHANDLED: {type(exc).__name__}: {exc}")
    return JSONResponse(status_code=500, content={
        "success": False,
        "error": "Internal server error",
    })


# CORS
origins = settings.allowed_origins_list
logger.info(f"CORS Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limit + Security Headers
@app.middleware("http")
async def middleware_stack(request: Request, call_next):
    start = time.time()

    if request.url.path.startswith("/api"):
        cid = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not cid:
            cid = request.client.host if request.client else "unknown"
        if rate_limiter.is_rate_limited(cid):
            return JSONResponse(status_code=429, content={"error": "Rate limited"})

    response = await call_next(request)
    elapsed = time.time() - start

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Process-Time"] = f"{elapsed:.4f}s"
    response.headers["X-ILRMF-Engine"] = "v1.0"

    return response


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(assess.router, prefix="/api/v1/assess", tags=["Assessment"])
app.include_router(payment.router, prefix="/api/v1/payment", tags=["Payment"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.get("/")
async def root():
    return {
        "service": "SAIF",
        "engine": "ILRMF v1.0",
        "creator": "Md Nazmul Islam (Bijoy)",
        "org": "NB TECH Bangladesh",
        "status": "production",
    }
'''

with open('backend/main.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(main_code)
print("OK: main.py")
