"""
SAIF ILRMF Core Engine - Groq + Gemini support
Creator: Md Nazmul Islam (Bijoy) | NB TECH | ILRMF
"""
import json
import re
import uuid
import time
from app.utils.config import get_settings
from app.utils.logger import logger

settings = get_settings()

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
        self._groq_client = None
        self._gemini_model = None
        self._provider = settings.AI_PROVIDER

    @property
    def groq_client(self):
        if self._groq_client is None:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=settings.GROQ_API_KEY)
                logger.info("Groq client initialized")
            except Exception as e:
                logger.error(f"Groq init failed: {e}")
                self._groq_client = None
        return self._groq_client

    @property
    def gemini_model(self):
        if self._gemini_model is None:
            try:
                import google.generativeai as genai
                if settings.GEMINI_API_KEY:
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    self._gemini_model = genai.GenerativeModel(
                        model_name=settings.GEMINI_MODEL,
                        generation_config=genai.GenerationConfig(
                            temperature=settings.GEMINI_TEMPERATURE,
                            max_output_tokens=settings.GEMINI_MAX_TOKENS,
                        ),
                    )
                    logger.info("Gemini model initialized (fallback)")
            except Exception as e:
                logger.error(f"Gemini init failed: {e}")
                self._gemini_model = None
        return self._gemini_model

    async def assess(self, dispute: dict, phase: int = 1) -> dict:
        phase = max(1, min(phase, 4))
        aid = f"ILRMF-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"ILRMF Assessment: {aid} | Phase={phase} | Provider={self._provider}")

        from app.ilrmf.fjr_engine import fjr_engine
        from app.validators.citation_checker import citation_checker
        from app.corpus.phase1_cases import PHASE1_CASES
        from app.corpus.statutes import STATUTES

        cases_str = ", ".join([f"{c.name} {c.citation}" for c in PHASE1_CASES])
        stat_str = ", ".join([f"{s.act} {s.section}" for s in STATUTES])
        prompt = SYSTEM_PROMPT.format(cases=cases_str, statutes=stat_str)
        prompt += "\n\nDISPUTE: " + json.dumps(dispute, default=str)

        raw_result = await self._call_ai(prompt)
        if not raw_result.get("success"):
            return raw_result

        parsed = raw_result["data"]

        # FJR integration
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
        parsed["governance"]["aiProvider"] = self._provider

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

        return {"success": True, "data": parsed, "assessment_id": aid, "phase": phase}

    async def _call_ai(self, prompt: str) -> dict:
        # Try Groq first, then Gemini fallback
        if self._provider == "groq" and self.groq_client:
            result = await self._call_groq(prompt)
            if result.get("success"):
                return result
            logger.warning("Groq failed, trying Gemini fallback")
        
        if self.gemini_model:
            result = await self._call_gemini(prompt)
            if result.get("success"):
                return result
            logger.warning("Gemini also failed")

        return {"success": False, "error": "All AI providers failed. Please try again in a minute."}

    async def _call_groq(self, prompt: str) -> dict:
        for attempt in range(3):
            try:
                response = self.groq_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "Return ONLY valid JSON. No markdown."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.1,
                    max_tokens=8192,
                )
                raw = response.choices[0].message.content.strip()
                if not raw:
                    raise ValueError("Empty response")
                parsed = self._parse_json(raw)
                logger.info(f"Groq OK: attempt={attempt+1} chars={len(raw)}")
                return {"success": True, "data": parsed}
            except Exception as e:
                logger.warning(f"Groq error (attempt {attempt+1}): {e}")
                if "429" in str(e) or "rate" in str(e).lower():
                    time.sleep(5 * (attempt + 1))
                else:
                    if attempt >= 2:
                        break

        return {"success": False, "error": "Groq failed after 3 attempts"}

    async def _call_gemini(self, prompt: str) -> dict:
        for attempt in range(2):
            try:
                response = self.gemini_model.generate_content(prompt)
                raw = response.text.strip()
                if not raw:
                    raise ValueError("Empty response")
                parsed = self._parse_json(raw)
                logger.info(f"Gemini OK: attempt={attempt+1} chars={len(raw)}")
                return {"success": True, "data": parsed}
            except Exception as e:
                logger.warning(f"Gemini error (attempt {attempt+1}): {e}")
                if "429" in str(e):
                    time.sleep(10 * (attempt + 1))

        return {"success": False, "error": "Gemini failed"}

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
