import json, re, uuid, time
import google.generativeai as genai
from app.ilrmf.fjr_engine import fjr_engine
from app.validators.citation_checker import citation_checker
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES
from app.utils.config import get_settings
from app.utils.logger import logger

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = '''
YOU ARE SAIF — UK Contract Law AI powered by ILRMF. Creator: Md Nazmul Islam (Bijoy), NB TECH.
VERIFIED CASES: {cases}
VERIFIED STATUTES: {statutes}
FJR TRIPLE-GATE ON EVERY CLAUSE. ZERO HALLUCINATION.
Return ONLY valid JSON: {{ "facts": {{...}}, "issues": [{{ "issue": "", "law": "", "fjr": {{"fair": bool, "just": bool, "reasonable": bool, "score": 0-100, "analysis": ""}}, "argument": {{"claimant": "", "defendant": ""}}, "verdict": "" }}], "relief": {{ "primary": "", "damages": "", "court": "", "probability": 0-100 }}, "governance": {{"hallucination": "ZERO", "engine": "ILRMF v1.0"}} }}
'''

class ILRMFEngine:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if not self._model:
            self._model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL, generation_config=genai.GenerationConfig(temperature=settings.GEMINI_TEMPERATURE, max_output_tokens=settings.GEMINI_MAX_TOKENS))
        return self._model

    async def assess(self, dispute: dict, phase: int = 1) -> dict:
        phase = max(1, min(phase, 4))
        aid = f"ILRMF-{uuid.uuid4().hex[:12].upper()}"
        raw_result = await self._call_gemini(dispute, phase)
        if not raw_result.get("success"): return raw_result
        parsed = raw_result["data"]
        
        # FJR integration
        for issue in parsed.get("issues", []):
            clause = dispute.get("disputedClause", "") or issue.get("issue", "")
            try:
                fjr = fjr_engine.assess_clause(clause=clause, contract_type=dispute.get("contractCategory", "B2B"), bargaining_power_equal=dispute.get("bargainingPower")=="equal", notice_adequate=dispute.get("noticeAdequate", True), standard_form=dispute.get("standardForm", False), value_of_contract=float(dispute.get("value") or 0), allows_unilateral_variation=dispute.get("allowsUnilateralVariation", False), consumer_vulnerable=dispute.get("consumerVulnerable", False))
                issue["fjr"] = {"fair": fjr.fair, "just": fjr.just, "reasonable": fjr.reasonable, "score": fjr.score, "analysis": fjr.analysis}
                if not fjr.fair or not fjr.just or not fjr.reasonable: issue["verdict"] = fjr.verdict
            except Exception as e: logger.warning(f"FJR error: {e}")
        
        validation = citation_checker.validate(parsed, phase)
        hallucination = "ZERO" if validation["passed"] else "FLAGGED"
        parsed.setdefault("governance", {})["citationValidation"] = validation
        parsed["governance"]["hallucination"] = hallucination
        parsed["governance"]["assessmentId"] = aid
        return {"success": True, "data": parsed, "assessment_id": aid, "phase": phase}

    async def _call_gemini(self, dispute: dict, phase: int) -> dict:
        cases_str = "
".join([f"- {c.name} {c.citation}" for c in PHASE1_CASES])
        stat_str = "
".join([f"- {s.act} {s.section}" for s in STATUTES])
        prompt = SYSTEM_PROMPT.format(cases=cases_str, statutes=stat_str) + f"
DISPUTE: {dispute}"
        try:
            resp = self.model.generate_content(prompt)
            raw = resp.text.strip()
            if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
            return {"success": True, "data": json.loads(raw)}
        except Exception as e:
            return {"success": False, "error": str(e)}

ilrmf_engine = ILRMFEngine()
