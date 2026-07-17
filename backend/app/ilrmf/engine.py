"""
SAIF ILRMF Core Engine — AI + Rule-Based Hybrid
Creator: Md Nazmul Islam (Bijoy) | NB TECH | ILRMF v1.1
"""
import json
import re
import uuid
import time
from app.utils.config import get_settings
from app.utils.logger import logger

settings = get_settings()

SYSTEM_PROMPT = """YOU ARE SAIF - UK Contract Law AI powered by ILRMF.
Creator: Md Nazmul Islam (Bijoy), NB TECH.
VERIFIED CASES (YOU MUST ONLY USE THESE PRINCIPLES):
{cases}
VERIFIED STATUTES:
{statutes}

FJR TRIPLE-GATE ON EVERY ISSUE. ZERO HALLUCINATION.

CRITICAL: Use FULL case names. Never truncate.
CORRECT: "Butler Machine Tool v Ex-Cell-O [1979] 1 WLR 401"
CORRECT: "Smith v Eric S Bush [1990] AC 831"
WRONG:   "Butler Machine Tool v Ex"
WRONG:   "Smith v Eric"

Return ONLY valid JSON. No markdown. No explanation outside JSON.

{{
  "facts": {{
    "parties": "Claimant vs Defendant",
    "contractType": "Commercial/Consumer/Employment",
    "consumerType": "B2B or B2C",
    "value": "£X",
    "bargainingPower": "equal or unequal",
    "standardForm": true/false,
    "disputedClause": "clause text or empty string",
    "summary": "2-3 sentence factual summary"
  }},
  "issues": [
    {{
      "issue": "The specific legal question",
      "law": "Full UK case citations with year and reporter. ONLY use principles from the VERIFIED CASES list above.",
      "fjr": {{
        "fair": true/false, "just": true/false, "reasonable": true/false,
        "score": 0-100, "fairScore": 0-100, "justScore": 0-100, "reasonableScore": 0-100,
        "analysis": "Detailed FJR analysis with case support (4+ sentences)"
      }},
      "argument": {{
        "claimant": "3-4 sentence argument with case law",
        "defendant": "3-4 sentence argument with case law"
      }},
      "verdict": "Clear verdict with legal basis"
    }}
  ],
  "relief": {{
    "primary": "Specific primary remedy",
    "secondary": "Specific secondary remedy",
    "damages": "Amount or method",
    "probability": 0-100,
    "reasoning": "Why this relief at this probability"
  }},
  "governance": {{"hallucination": "ZERO", "engine": "ILRMF v1.1"}}
}}

RULES:
- FULL case names only — never truncate
- Every issue needs law with full citations
- Every issue needs claimant AND defendant arguments (3+ sentences)
- Every issue needs FJR analysis (4+ sentences)
- Only use the legal principles provided in the VERIFIED CASES list. Do NOT apply external knowledge to these cases.
- If unsure, omit rather than guess

STRICT BREACH, DEBT, AND DAMAGES RULES:
- When a party clearly states they will not perform, this is REPUDIATION (Hochster v De La Tour).
- NEVER award "Specific Performance" for service contracts (web dev, consulting, freelancing). English courts refuse to force personal service.
- DEBT VS DAMAGES: If a milestone was reached, or a 'deemed acceptance' timeframe expired without rejection, the milestone payment becomes an absolute DEBT. Do NOT use Quantum Meruit for completed milestones.
- QUANTUM MERUIT: Only use Quantum Meruit if (a) there is no valid contract covering the work, OR (b) the contract was terminated BEFORE a specific milestone was reached (partial completion).
- LOST PROFITS: Lost opportunities are ONLY recoverable if communicated to the defendant at contract formation (Hadley v Baxendale). Otherwise, they are too remote.
- LATE PAYMENT: In B2B, if a valid invoice is unpaid, automatically apply the Late Payment of Commercial Debts Act 1998 (8% statutory interest).
- ACCEPTANCE TESTING: If the buyer rejects software for reasons NOT in the Statement of Work (SOW), rule the rejection invalid under Sopar Group v Walker. If a contract gives 'final and binding' discretion to the buyer, apply Bristol Airport v Powdrill (must be exercised rationally).
- IP DISPUTES: If a freelancer created code and wasn't paid, check for a written IP assignment. If none exists, apply Robin Ray v Classic FM (freelancer keeps copyright, client only gets implied license).
"""


class IncorporationGate:
    @staticmethod
    def evaluate(facts: dict) -> dict:
        score = 50
        reasons = []
        # Combine clause text and summary for semantic analysis
        clause_text = str(facts.get("disputedClause", "") + " " + facts.get("summary", "")).lower()
        
        if facts.get("rushedSignature"):
            score -= 20
            reasons.append("Pressure to sign quickly weakens implied notice (Thornton v Shoe Lane).")
        if not facts.get("specificNotice"):
            score -= 25
            reasons.append("No specific notice of onerous term given (Interfoto v Stiletto).")
            
        # SMART SEMANTIC CHECKS (v1.1 Upgrade)
        if "schedule" in clause_text and ("attached" in clause_text or "appendix" in clause_text):
            score -= 20
            reasons.append("Onerous terms hidden in an attached Schedule/Appendix without specific reference.")
            facts["buriedClause"] = True # Auto-flag as buried
            
        if "not drawn to attention" in clause_text or "not highlighted" in clause_text:
            score -= 15
            reasons.append("Evidence terms were not brought to the other party's attention.")
            facts["buriedClause"] = True

        if facts.get("buriedClause"):
            score -= 15
            reasons.append("Clause buried in document, not prominent (Thornton v Shoe Lane).")
            
        if facts.get("signedDocument"):
            score += 30
            reasons.append("Signed document creates baseline incorporation (L'Estrange v Graucob).")
            
        if facts.get("standardForm") and not facts.get("specificNotice"):
            score -= 10
            reasons.append("Standard form contract without specific notice — heightened scrutiny.")
            
        score = max(0, min(100, score))
        # Changed logic: If it's buried, it fails regardless of baseline score
        incorporated = score >= 60 and not facts.get("buriedClause", False) 
        return {
            "incorporated": incorporated, "score": score, "reasons": reasons,
            "keyCases": ["Thornton v Shoe Lane Parking [1971] 2 QB 163", "L'Estrange v Graucob [1934] 2 KB 394", "Interfoto Picture Library v Stiletto [1989] QB 433"],
        }


class FJRDynamicScorer:
    @staticmethod
    def apply_overrides(issue: dict, fjr_scores: dict, facts: dict) -> dict:
        scores = dict(fjr_scores)
        overrides = []
        law_text = str(issue.get("law", ""))
        if "s.2(1)" in law_text and ("personal injury" in law_text.lower() or "death" in law_text.lower()):
            scores["reasonable"] = False
            scores["reasonableScore"] = 0
            scores["score"] = 0
            overrides.append("UCTA s.2(1) absolute bar applied — personal injury exclusion void regardless of reasonableness.")
        if "unilateral variation" in law_text.lower() or "variation" in str(issue.get("issue", "")).lower():
            if facts.get("isConsumer") or not facts.get("bargainingEqual", True):
                if scores["fairScore"] > 20:
                    scores["fairScore"] = max(0, scores["fairScore"] - 30)
                    scores["justScore"] = max(0, scores["justScore"] - 25)
                    overrides.append("Unilateral variation clause in unequal/consumer context — FJR scores reduced (CRA 2015 Sch.2 Para 4).")
        scores["score"] = (scores["fairScore"] + scores["justScore"] + scores["reasonableScore"]) // 3
        scores["fair"] = scores["fairScore"] >= 50
        scores["just"] = scores["justScore"] >= 50
        scores["reasonable"] = scores["reasonableScore"] >= 50
        scores["overrides"] = overrides
        return scores


class ProbabilityCalibrator:
    @staticmethod
    def calculate(verdict: str, issues: list, facts: dict, incorporation: dict) -> dict:
        if verdict == "VALID":
            return {"probability": 15, "confidence": "Low", "explanation": "Clause deemed valid/enforceable. Low probability of successful challenge."}
        if verdict == "NOT INCORPORATED":
            return {"probability": 85, "confidence": "High", "explanation": "Clause not incorporated into contract. Strong position for claimant."}
        base = 65
        reasons = [f"Base probability {base}% due to {verdict} verdict."]
        if any("s.2(1)" in str(i.get("law", "")) for i in issues):
            base = 95
            reasons.append("UCTA s.2(1) absolute bar on personal injury exclusion — near-certain void.")
        if facts.get("isConsumer"):
            base = min(95, base + 10)
            reasons.append("CRA 2015 consumer-friendly interpretation applied.")
        if not incorporation.get("incorporated", True):
            base = min(95, base + 5)
            reasons.append("Incorporation failure further strengthens claimant position.")
        if facts.get("evidenceQuality") == "weak":
            base -= 15
            reasons.append("Weak evidence quality reduces certainty.")
        final = max(5, min(95, base))
        return {"probability": final, "confidence": "High" if final > 70 else "Moderate" if final > 40 else "Low", "explanation": " ".join(reasons)}


class CourtAssigner:
    @staticmethod
    def assign(claim_value: float) -> dict:
        if claim_value <= 10000:
            return {"track": "Small Claims Track", "court": "County Court", "details": "Informal procedure, costs capped."}
        elif claim_value <= 25000:
            return {"track": "Fast Track", "court": "County Court", "details": "Standard directions, fixed costs, trial usually 1 day."}
        elif claim_value <= 100000:
            return {"track": "Intermediate Track", "court": "County Court", "details": "CPR 26A — expanded standard directions."}
        return {"track": "Multi-Track", "court": "County Court or High Court (KBD)", "details": "Complex cases, full costs budgeting."}


class ReliefGenerator:
    @staticmethod
    def generate(verdict: str, facts: dict, court: dict) -> dict:
        claim_value = facts.get("claimValue", "TBD")
        law_hints = str(facts.get("lawHints", "")).lower()
        summary = str(facts.get("summary", "")).lower()
        
        # NEW: B2B Late Payment Trigger
        if facts.get("isConsumer") == False and ("unpaid" in summary or "invoice" in summary):
            return {
                "primary": "Recovery of unpaid invoice as a liquidated debt",
                "secondary": "Statutory interest under Late Payment of Commercial Debts Act 1998 (8% above base rate) plus fixed recovery costs",
                "damages": claim_value,
                "interest": "Statutory (LPCD Act 1998)"
            }

        # NEW: IP Infringement Trigger
        if "copyright" in law_hints or "ip" in law_hints or "robin ray" in law_hints:
            return {
                "primary": "Declaration that Claimant retains copyright; Injunction preventing Defendant from using or selling the work to third parties",
                "secondary": "Account of profits or damages for copyright infringement",
                "damages": "To be assessed (Account of Profits)",
                "interest": "Statutory interest under Senior Courts Act 1981 s.35A"
            }

        if verdict == "NOT INCORPORATED":
            return {"primary": "Declaration that the clause was not incorporated and is not binding", "secondary": "Contract performed on basis of implied/reasonable terms", "damages": claim_value, "interest": "Statutory interest under Senior Courts Act 1981 s.35A at 8% per annum"}
        if verdict == "VALID":
            return {"primary": "N/A — clause upheld as valid and enforceable", "secondary": "N/A", "damages": "N/A", "interest": "N/A"}
        has_pi = "personal injury" in str(facts.get("lawHints", ""))
        if has_pi:
            return {"primary": "Declaration that exclusion clause is void under UCTA 1977 s.2(1)", "secondary": "Full damages for personal injury/death without cap", "damages": "Uncapped — to be assessed by court", "interest": "Statutory interest under Senior Courts Act 1981 s.35A"}
        
        return {"primary": "Declaration that the clause is void and unenforceable under UCTA 1977/CRA 2015", "secondary": "Damages assessed on ordinary contractual principles (Hadley v Baxendale)", "damages": claim_value, "interest": "Statutory interest under Senior Courts Act 1981 s.35A at 8% per annum"}


def _normalize_response(parsed: dict, dispute: dict) -> dict:
    claim_value = float(dispute.get("value") or 0)
    facts = parsed.get("facts", {})
    if not isinstance(facts, dict):
        facts = {}
    facts.setdefault("parties", f"{dispute.get('claimant', '')} vs {dispute.get('defendant', '')}")
    facts.setdefault("contractType", dispute.get("contractType", "N/A"))
    facts.setdefault("consumerType", dispute.get("contractCategory", "N/A"))
    facts.setdefault("value", f"£{claim_value:,.0f}" if claim_value else "N/A")
    facts.setdefault("bargainingPower", dispute.get("bargainingPower", "N/A"))
    facts.setdefault("standardForm", dispute.get("standardForm", False))
    facts.setdefault("disputedClause", dispute.get("disputedClause", ""))
    facts.setdefault("summary", "")
    parsed["facts"] = facts
    issues = parsed.get("issues", [])
    if not isinstance(issues, list):
        issues = []
    normalized = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue.setdefault("issue", "Not specified")
        issue.setdefault("law", "Not specified by engine")
        fjr = issue.get("fjr", {})
        if not isinstance(fjr, dict):
            fjr = {}
        fjr.setdefault("fair", False)
        fjr.setdefault("just", False)
        fjr.setdefault("reasonable", False)
        fjr.setdefault("score", 50)
        fjr.setdefault("fairScore", 50)
        fjr.setdefault("justScore", 50)
        fjr.setdefault("reasonableScore", 50)
        fjr.setdefault("analysis", "No detailed analysis provided")
        issue["fjr"] = fjr
        arg = issue.get("argument", {})
        if not isinstance(arg, dict):
            arg = {}
        arg.setdefault("claimant", "No argument provided")
        arg.setdefault("defendant", "No argument provided")
        issue["argument"] = arg
        issue.setdefault("verdict", "Not assessed")
        normalized.append(issue)
    parsed["issues"] = normalized
    relief = parsed.get("relief", {})
    if not isinstance(relief, dict):
        relief = {}
    relief.setdefault("primary", "N/A")
    relief.setdefault("secondary", "N/A")
    relief.setdefault("damages", f"£{claim_value:,.0f}" if claim_value else "TBD")
    relief.setdefault("probability", 50)
    relief.setdefault("reasoning", "")
    parsed["relief"] = relief
    gov = parsed.get("governance", {})
    if not isinstance(gov, dict):
        gov = {}
    gov.setdefault("hallucination", "UNKNOWN")
    gov.setdefault("engine", "ILRMF v1.1")
    parsed["governance"] = gov
    return parsed


def _build_v2_facts(dispute: dict, issues: list) -> dict:
    return {
        "claimValue": f"£{float(dispute.get('value') or 0):,.0f}",
	"summary": dispute.get("summary", ""),
        "bargainingEqual": dispute.get("bargainingPower") == "equal",
        "isConsumer": dispute.get("contractCategory") == "B2C",
        "standardForm": dispute.get("standardForm", False),
        "specificNotice": dispute.get("noticeAdequate", True),
        "signedDocument": not bool(dispute.get("disputedClause", "").strip()) or dispute.get("standardForm", False),
        "rushedSignature": False, "buriedClause": False, "evidenceQuality": "standard",
        "requiresInjunction": False, "lawHints": " ".join(str(i.get("law", "")) for i in issues),
    }


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
                        generation_config=genai.GenerationConfig(temperature=settings.GEMINI_TEMPERATURE, max_output_tokens=settings.GEMINI_MAX_TOKENS),
                    )
                    logger.info("Gemini model initialized (fallback)")
            except Exception as e:
                logger.error(f"Gemini init failed: {e}")
        return self._gemini_model

    async def assess(self, dispute: dict, phase: int = 1) -> dict:
        phase = max(1, min(phase, 4))
        aid = f"ILRMF-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"ILRMF Assessment: {aid} | Phase={phase} | Provider={self._provider}")
        from app.ilrmf.fjr_engine import fjr_engine
        from app.validators.citation_checker import citation_checker
        from app.corpus.phase1_cases import PHASE1_CASES
        from app.corpus.statutes import STATUTES
        
        # FIX: Feed principles and key holdings to the AI, not just names
        cases_str = "\n".join([f"- {c.name} ({c.citation}): {c.principle}. KEY HOLDING: {c.key_holding}" for c in PHASE1_CASES])
        
        # FIX: Feed key rules to the AI for statutes
        stat_str = "\n".join([f"- {s.act} {s.section} ({s.title}): {s.key_rule}" for s in STATUTES])
        
        prompt = SYSTEM_PROMPT.format(cases=cases_str, statutes=stat_str)
        prompt += "\n\nDISPUTE: " + json.dumps(dispute, default=str)
        raw_result = await self._call_ai(prompt)
        if not raw_result.get("success"):
            return raw_result
        parsed = raw_result["data"]
        parsed = _normalize_response(parsed, dispute)
        v2_facts = _build_v2_facts(dispute, parsed.get("issues", []))
        incorporation = {"incorporated": True, "score": 100, "reasons": [], "keyCases": []}
        if dispute.get("disputedClause", "").strip():
            incorporation = IncorporationGate.evaluate(v2_facts)
            logger.info(f"Incorporation Gate: incorporated={incorporation['incorporated']} score={incorporation['score']}")
        for issue in parsed.get("issues", []):
            clause = dispute.get("disputedClause", "") or issue.get("issue", "")
            try:
                fjr = fjr_engine.assess_clause(
                    clause=clause, contract_type=dispute.get("contractCategory", "B2B"),
                    bargaining_power_equal=dispute.get("bargainingPower") == "equal",
                    notice_adequate=dispute.get("noticeAdequate", True),
                    standard_form=dispute.get("standardForm", False),
                    value_of_contract=float(dispute.get("value") or 0),
                    allows_unilateral_variation=dispute.get("allowsUnilateralVariation", False),
                    consumer_vulnerable=dispute.get("consumerVulnerable", False),
                )
                base_fjr = {"fair": fjr.fair, "just": fjr.just, "reasonable": fjr.reasonable, "score": fjr.score, "fairScore": fjr.fair_score, "justScore": fjr.just_score, "reasonableScore": fjr.reasonable_score, "analysis": fjr.analysis}
            except Exception as e:
                logger.warning(f"FJR engine error: {e}")
                base_fjr = issue.get("fjr", {})
            enhanced_fjr = FJRDynamicScorer.apply_overrides(issue, base_fjr, v2_facts)
            if enhanced_fjr.get("overrides"):
                for o in enhanced_fjr["overrides"]:
                    logger.info(f"FJR Override: {o}")
            if not incorporation["incorporated"]:
                enhanced_fjr["incorporationNote"] = "Clause not incorporated — automatically unenforceable."
                issue["verdict"] = f"NOT INCORPORATED: {incorporation['reasons'][0] if incorporation['reasons'] else 'Failed incorporation test'}"
            elif not enhanced_fjr["fair"] or not enhanced_fjr["just"] or not enhanced_fjr["reasonable"]:
                if not issue["verdict"] or issue["verdict"] == "Not assessed":
                    issue["verdict"] = fjr.verdict if hasattr(fjr, 'verdict') else "Clause fails FJR Triple-Gate — potentially void and unenforceable."
            overrides = enhanced_fjr.pop("overrides", [])
            issue["fjr"] = enhanced_fjr
            if overrides:
                issue["fjr"]["analysis"] += "\n\n" + " ".join(overrides)
        issues = parsed.get("issues", [])
        any_void = any("VOID" in str(i.get("verdict", "")) for i in issues)
        any_likely_void = any("LIKELY VOID" in str(i.get("verdict", "")) for i in issues)
        any_not_incorporated = any("NOT INCORPORATED" in str(i.get("verdict", "")) for i in issues)
        if any_not_incorporated:
            overall_verdict = "NOT INCORPORATED"
        elif any_void:
            overall_verdict = "VOID"
        elif any_likely_void:
            overall_verdict = "LIKELY VOID"
        else:
            overall_verdict = "VALID"
        claim_value = float(dispute.get("value") or 0)
        court = CourtAssigner.assign(claim_value)
        logger.info(f"Court: {court['track']} — {court['court']}")
        probability = ProbabilityCalibrator.calculate(overall_verdict, issues, v2_facts, incorporation)
        logger.info(f"Probability: {probability['probability']}% ({probability['confidence']})")
        rule_relief = ReliefGenerator.generate(overall_verdict, v2_facts, court)
        ai_relief = parsed.get("relief", {})
        # ALWAYS use AI's primary/secondary/damages/reasoning if provided
        # ALWAYS use rule-based court assignment (AI often gets this wrong)
        # ALWAYS use AI's probability for non-unfair-terms cases
        if ai_relief.get("reasoning") and len(ai_relief.get("reasoning", "")) > 20:
            ai_relief["court"] = f"{court['track']} — {court['court']}"
            ai_relief.setdefault("interest", rule_relief.get("interest", "N/A"))
            ai_relief.setdefault("secondary", rule_relief.get("secondary", "N/A"))
            parsed["relief"] = ai_relief
        else:
            rule_relief["probability"] = probability["probability"]
            rule_relief["reasoning"] = probability["explanation"]
            rule_relief["court"] = f"{court['track']} — {court['court']}"
            parsed["relief"] = rule_relief
        validation = citation_checker.validate(parsed, phase)
        hallucination = "ZERO" if validation["passed"] else "FLAGGED"
        parsed["governance"].update({
            "citationValidation": validation, "hallucination": hallucination,
            "assessmentId": aid, "creator": "Md Nazmul Islam (Bijoy)", "org": "NB TECH Bangladesh",
            "phase": phase, "aiProvider": self._provider, "courtTrack": court["track"],
            "courtDetails": court["details"], "overallVerdict": overall_verdict,
            "incorporation": incorporation, "probabilityConfidence": probability["confidence"],
            "pipeline": "AI + Rule-Based Hybrid",
        })
        logger.info(f"ILRMF Complete: {aid} | Verdict={overall_verdict} | P={parsed['relief'].get('probability', '?')}% | Hallucination={hallucination} | Issues={len(issues)}")
        return {"success": True, "data": parsed, "assessment_id": aid, "phase": phase}

    async def _call_ai(self, prompt: str) -> dict:
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
                    messages=[{"role": "system", "content": "Return ONLY valid JSON. No markdown."}, {"role": "user", "content": prompt}],
                    temperature=0.1, max_tokens=8192,
                )
                raw = response.choices[0].message.content.strip()
                if not raw:
                    raise ValueError("Empty response")
                parsed = self._parse_json(raw)
                logger.info(f"Groq OK: attempt={attempt + 1} chars={len(raw)}")
                return {"success": True, "data": parsed}
            except Exception as e:
                logger.warning(f"Groq error (attempt {attempt + 1}): {e}")
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
                logger.info(f"Gemini OK: attempt={attempt + 1} chars={len(raw)}")
                return {"success": True, "data": parsed}
            except Exception as e:
                logger.warning(f"Gemini error (attempt {attempt + 1}): {e}")
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
            return {"facts": {"parse_error": True}, "issues": [], "relief": {}, "governance": {"hallucination": "PARSE_ERROR"}}


ilrmf_engine = ILRMFEngine()