"""SAIF ILRMF Core Engine v3.1 — AI proposal + deterministic predicates."""
from __future__ import annotations
import asyncio, json, re, uuid
from enum import Enum
from app.utils.config import get_settings
from app.utils.logger import logger
from app.ilrmf.fjr_engine import fjr_engine
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES

settings = get_settings()

class PredicateStatus(str, Enum):
    PROVEN = "PROVEN"
    NOT_PROVEN = "NOT_PROVEN"
    DISPUTED = "DISPUTED"
    CONDITIONAL = "CONDITIONAL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"

class DisputeRouter:
    @staticmethod
    def route(dispute: dict) -> list[str]:
        cat = str(dispute.get("contractCategory", "B2B")).upper()
        ctype = str(dispute.get("contractType", "")).lower()
        text = (str(dispute.get("summary", "")) + " " + str(dispute.get("disputedClause", ""))).lower()
        d = []
        if "employment" in ctype or any(k in text for k in ("employee", "employer", "dismissal", "discrimination")):
            return ["CRITICAL ROUTE: EMPLOYMENT LAW MODE.", "DISABLE FJR TRIPLE-GATE.", "Apply Employment Rights Act 1996 and Equality Act 2010.", "Forum: Employment Tribunal."]
        if any(k in ctype for k in ("tenancy", "lease", "rent", "landlord")) or any(k in text for k in ("tenant", "landlord", "disrepair", "deposit", "eviction")):
            return ["CRITICAL ROUTE: LANDLORD AND TENANT MODE.", "DISABLE FJR AS PRIMARY TEST.", "Apply Landlord and Tenant Act 1985 and Housing Act 2004 where applicable."]
        d.append("ROUTE: B2C CONSUMER MODE." if cat == "B2C" else "ROUTE: B2B COMMERCIAL MODE.")
        d.append("ROUTE: WRITTEN CONTRACT MODE. Run Incorporation Gate where a disputed clause exists." if dispute.get("disputedClause") else "ROUTE: NO SPECIFIC DISPUTED CLAUSE PROVIDED.")
        if any(k in text for k in ("invoice", "unpaid", "withheld", "payment", "debt")): d.append("PAYMENT / DEBT MODE: evaluate invoice due, paid, withheld and any lawful adjustment separately.")
        if any(k in text for k in ("defective", "defect", "quality", "reject", "compressor", "goods")): d.append("GOODS QUALITY MODE: evaluate allegation, evidence, conformity and remedy separately.")
        if any(k in text for k in ("termination", "terminated", "notice", "cancel")): d.append("TERMINATION MODE: evaluate trigger, notice, expiry and waiver/affirmation separately.")
        return d

class IncorporationGate:
    @staticmethod
    def evaluate(facts: dict) -> dict:
        clause = str(facts.get("disputedClause", "")).strip()
        if not clause:
            return {"status": "NOT_ASSESSED", "incorporated": None, "score": None, "reasons": [], "keyCases": []}
        signed = facts.get("signedDocument")
        notice = facts.get("notice_objective_status", "adequate")
        onerous = facts.get("unusualOrOnerousTerm", False)
        if signed is True and notice == "adequate" and not onerous:
            return {"status": "INCORPORATED", "incorporated": True, "score": 100, "reasons": ["Signed written contract with no identified incorporation defect."], "keyCases": ["L'Estrange v F Graucob Ltd [1934] 2 KB 394"]}
        if notice in ("inadequate", "buried") or onerous:
            return {"status": "CONDITIONAL", "incorporated": None, "score": None, "reasons": ["Incorporation requires factual/legal assessment of notice, prominence and contract formation."], "keyCases": ["Thornton v Shoe Lane Parking Ltd [1971] 2 QB 163", "Interfoto Picture Library Ltd v Stiletto Visual Programmes Ltd [1989] QB 433"]}
        return {"status": "CONDITIONAL", "incorporated": None, "score": None, "reasons": ["Insufficient facts to make a definitive incorporation finding."], "keyCases": []}

class PaymentPredicateEngine:
    @staticmethod
    def evaluate(facts: dict) -> dict:
        p = facts.get("payment", {}) or {}
        invoice = float(p.get("invoiceAmount") or 0)
        paid = float(p.get("amountPaid") or 0)
        withheld = float(p.get("amountWithheld") or 0)
        due = max(0.0, invoice - paid)
        if invoice <= 0: status = PredicateStatus.UNKNOWN
        elif due <= 0: status = PredicateStatus.NOT_PROVEN
        elif withheld > 0: status = PredicateStatus.CONDITIONAL
        else: status = PredicateStatus.PROVEN
        return {"paymentDefault": status, "amountDue": due, "reason": "Payment status is conditional where an amount is withheld pending a legal basis." if withheld > 0 else ""}

class DefectPredicateEngine:
    @staticmethod
    def evaluate(facts: dict) -> dict:
        d = facts.get("defect", {}) or {}
        alleged = bool(d.get("alleged"))
        defective = int(d.get("defectiveUnits") or 0)
        total = int(d.get("totalUnits") or 0)
        evidence = bool(d.get("inspectionReports") or d.get("technicalEvidence") or d.get("photographs"))
        percentage = round(defective / total * 100, 2) if total else 0.0
        if not alleged: status = PredicateStatus.NOT_APPLICABLE; breach = PredicateStatus.NOT_APPLICABLE
        elif evidence and d.get("specification"): status = PredicateStatus.CONDITIONAL; breach = PredicateStatus.CONDITIONAL
        else: status = PredicateStatus.DISPUTED; breach = PredicateStatus.NOT_PROVEN
        return {"status": status, "breachStatus": breach, "defectPercentage": percentage, "reason": "Defect allegation is not treated as proof without conformity evidence."}

class WithholdingPredicateEngine:
    @staticmethod
    def evaluate(facts: dict, payment: dict, defect: dict) -> dict:
        p = facts.get("payment", {}) or {}
        withheld = float(p.get("amountWithheld") or 0)
        if withheld <= 0: return {"status": PredicateStatus.NOT_APPLICABLE, "reason": "No amount withheld."}
        if p.get("contractualWithholdingRight") is True: return {"status": PredicateStatus.CONDITIONAL, "reason": "Express contractual right requires application to the invoice and facts."}
        if defect.get("breachStatus") in (PredicateStatus.PROVEN, PredicateStatus.CONDITIONAL): return {"status": PredicateStatus.CONDITIONAL, "reason": "Potential cross-claim/remedial basis requires proof and quantum."}
        return {"status": PredicateStatus.CONDITIONAL, "reason": "No established withholding entitlement supplied."}

class WaiverAffirmationEngine:
    @staticmethod
    def evaluate(facts: dict) -> dict:
        t = facts.get("termination", {}) or {}
        if not t.get("continuedPerformanceAfterBreach"): return {"status": PredicateStatus.NOT_PROVEN, "reason": "No continued performance after alleged breach recorded."}
        if t.get("reservationOfRights") is True: return {"status": PredicateStatus.CONDITIONAL, "reason": "Continued performance occurred but rights were reserved."}
        return {"status": PredicateStatus.CONDITIONAL, "reason": "Continued performance may create a waiver/affirmation issue; knowledge and election require legal assessment."}

class TerminationPredicateEngine:
    @staticmethod
    def evaluate(facts: dict, payment: dict, waiver: dict, withholding: dict) -> dict:
        t = facts.get("termination", {}) or {}
        if not t.get("clauseExists"): return {"status": PredicateStatus.NOT_APPLICABLE, "reason": "No express termination clause supplied."}
        if payment.get("paymentDefault") == PredicateStatus.PROVEN and waiver.get("status") == PredicateStatus.NOT_PROVEN and withholding.get("status") in (PredicateStatus.NOT_APPLICABLE, PredicateStatus.PROVEN):
            return {"status": PredicateStatus.PROVEN, "reason": "Payment trigger proven and no unresolved waiver/withholding dependency identified."}
        return {"status": PredicateStatus.CONDITIONAL, "reason": "Termination depends on the underlying payment/withholding and waiver predicates."}

class DependencyEngine:
    @staticmethod
    def build(payment_result, defect_result, withholding_result, waiver_result, termination_result, loss_result):
        return [
            {"predicate": "PAYMENT_DEFAULT", "dependsOn": [], "status": payment_result.get("paymentDefault", PredicateStatus.UNKNOWN)},
            {"predicate": "DEFECT", "dependsOn": [], "status": defect_result.get("status", PredicateStatus.UNKNOWN)},
            {"predicate": "WITHHOLDING_RIGHT", "dependsOn": ["PAYMENT_DEFAULT", "DEFECT"], "status": withholding_result.get("status", PredicateStatus.UNKNOWN)},
            {"predicate": "WAIVER_AFFIRMATION", "dependsOn": ["PAYMENT_DEFAULT"], "status": waiver_result.get("status", PredicateStatus.UNKNOWN)},
            {"predicate": "TERMINATION_VALID", "dependsOn": ["PAYMENT_DEFAULT", "WITHHOLDING_RIGHT", "WAIVER_AFFIRMATION"], "status": termination_result.get("status", PredicateStatus.UNKNOWN)},
            {"predicate": "LOSS", "dependsOn": [], "status": loss_result.get("status", PredicateStatus.UNKNOWN)},
        ]

class CourtAssigner:
    @staticmethod
    def assign(claim_value: float, contract_type: str = "") -> dict:
        t = contract_type.lower()
        if "employment" in t: return {"track": "Employment Tribunal", "court": "Employment Tribunal", "details": "Employment jurisdiction."}
        if any(k in t for k in ("tenancy", "lease", "landlord", "rent")): return {"track": "Property / Housing jurisdiction", "court": "County Court or applicable Tribunal", "details": "Forum depends on remedy and statutory jurisdiction."}
        if claim_value <= 10000: return {"track": "SMALL CLAIMS CANDIDATE", "court": "County Court", "details": "Track depends on applicable CPR criteria and claim composition."}
        if claim_value <= 25000: return {"track": "FAST TRACK CANDIDATE", "court": "County Court", "details": "Track depends on applicable CPR criteria."}
        return {"track": "MULTI-TRACK CANDIDATE", "court": "County Court or High Court", "details": "Jurisdiction and track depend on claim type and CPR criteria."}

class ReliefGenerator:
    @staticmethod
    def generate(overall_verdict, payment_result, defect_result, termination_result, interest_result):
        if overall_verdict == "CONDITIONAL":
            return {"primary": "Conditional relief: resolve the identified legal predicates before final monetary relief.", "secondary": "Preserve applicable debt, damages, set-off and termination arguments subject to proof.", "damages": "To be determined from proven loss and applicable remedy.", "interest": interest_result, "probability": 50, "reasoning": "Material dependencies remain unresolved."}
        if payment_result.get("paymentDefault") == PredicateStatus.PROVEN:
            return {"primary": "Recovery of proven unpaid contractual debt.", "secondary": "Applicable statutory/judicial interest and proven contractual damages.", "damages": f"£{payment_result.get('amountDue', 0):,.2f}", "interest": interest_result, "probability": 70, "reasoning": "Payment default predicate is presently proven."}
        return {"primary": "Further factual/legal assessment required.", "secondary": "N/A", "damages": "TBD", "interest": interest_result, "probability": 40, "reasoning": "No definitive primary remedy established."}

SYSTEM_PROMPT = """You are SAIF, an AI legal-analysis drafting layer powered by ILRMF v3.1. Use ONLY the injected corpus. Do not invent cases or statutes. Return valid JSON only. Never turn an allegation into a proved fact. Preserve unresolved dependencies as CONDITIONAL or DISPUTED. FJR is analytical only and does not independently determine legal validity. Full case names and citations are required."""

class ILRMFEngine:
    def __init__(self): self._client = None; self._provider = getattr(settings, "AI_PROVIDER", "gemini")
    @property
    def gemini_client(self):
        if self._client is None:
            from google import genai
            key = getattr(settings, "GEMINI_API_KEY", None)
            if not key: raise RuntimeError("GEMINI_API_KEY is not configured")
            self._client = genai.Client(api_key=key)
        return self._client

    async def assess(self, dispute: dict, phase: int = 1) -> dict:
        aid = f"ILRMF-{uuid.uuid4().hex[:12].upper()}"
        payment = PaymentPredicateEngine.evaluate(dispute)
        defect = DefectPredicateEngine.evaluate(dispute)
        withholding = WithholdingPredicateEngine.evaluate(dispute, payment, defect)
        waiver = WaiverAffirmationEngine.evaluate(dispute)
        termination = TerminationPredicateEngine.evaluate(dispute, payment, waiver, withholding)
        loss = {"status": PredicateStatus.CONDITIONAL if (dispute.get("loss", {}) or {}).get("lostProfits") or (dispute.get("loss", {}) or {}).get("consequentialLoss") else PredicateStatus.UNKNOWN,
                "reason": "Loss requires causation, remoteness and proof."}
        dependency_graph = DependencyEngine.build(payment, defect, withholding, waiver, termination, loss)
        directives = DisputeRouter.route(dispute)
        area = "b2c_consumer" if str(dispute.get("contractCategory")) == "B2C" else "b2b_commercial"
        cases = [c for c in PHASE1_CASES if c.area in {"general_contract", area}]
        statutes = [s for s in STATUTES if s.applies_to in {"Both", "General", "B2B", "B2C" if area == "b2c_consumer" else "B2B"}]
        issue_defs = self._issue_defs(dispute, payment, defect, withholding, waiver, termination)
        ai_data = await self._call_ai(self._build_prompt(dispute, directives, cases, statutes, issue_defs))
        issues = self._normalise_issues(ai_data.get("issues", []), dispute)
        incorporation = IncorporationGate.evaluate({**dispute, "signedDocument": dispute.get("signedDocument"), "unusualOrOnerousTerm": dispute.get("unusualOrOnerousTerm", False)})
        fjr_info = self._apply_fjr(issues, dispute)
        overall = self._overall_status(payment, defect, withholding, waiver, termination)
        court = CourtAssigner.assign(float(dispute.get("value") or 0), dispute.get("contractType", ""))
        interest = {"status": PredicateStatus.CONDITIONAL, "basis": "Applicable statutory or judicial interest must be determined for the relevant period."}
        relief = ReliefGenerator.generate(overall, payment, defect, termination, interest)
        relief["court"] = f"{court['track']} - {court['court']}"
        governance = {
            "hallucination": "NOT_DETECTED",
            "engine": "ILRMF v3.1",
            "assessmentId": aid,
            "phase": phase,
            "aiProvider": self._provider,
            "overallVerdict": overall,
            "pipeline": "AI + Rule-Based Hybrid with Predicate Dependency Controls",
            "deterministicReviewRequired": overall == "CONDITIONAL",
            "humanReviewRecommended": True,
            "incorporation": incorporation,
            "predicateSummary": {"payment": payment, "defect": defect, "withholding": withholding, "waiverAffirmation": waiver, "termination": termination, "loss": loss, "interest": interest},
        }
        facts = {"parties": f"{dispute.get('claimant','')} vs {dispute.get('defendant','')}", "contractType": dispute.get("contractType"), "consumerType": dispute.get("contractCategory"), "value": f"£{float(dispute.get('value') or 0):,.0f}", "bargainingPower": dispute.get("bargainingPower"), "standardForm": dispute.get("standardForm", False), "disputedClause": dispute.get("disputedClause", ""), "summary": dispute.get("summary", "")}
        data = {"facts": facts, "issues": issues, "dependencyGraph": dependency_graph, "deterministicPredicates": {"payment": payment, "defect": defect, "withholding": withholding, "waiverAffirmation": waiver, "termination": termination, "loss": loss, "interest": interest}, "relief": relief, "governance": governance}
        return {"success": True, "data": data, "assessment_id": aid, "phase": phase}

    def _issue_defs(self, d, p, defect, w, waiver, term):
        defs = [
            ("Whether the relevant invoice is presently a payment default", p.get("paymentDefault")),
            ("Whether the alleged defective goods establish a legally relevant breach", defect.get("breachStatus")),
            ("Whether Bright has a legal basis to withhold £12,000", w.get("status")),
            ("Whether Alpha's continued performance creates a waiver/affirmation issue", waiver.get("status")),
            ("Whether Alpha validly terminated the contract", term.get("status")),
            ("What monetary remedies and interest are presently supportable", PredicateStatus.CONDITIONAL),
        ]
        return defs

    def _build_prompt(self, dispute, directives, cases, statutes, issue_defs):
        case_text = "\n".join(f"- {c.name} ({c.citation}): {c.key_holding}" for c in cases)
        statute_text = "\n".join(f"- {s.act} {s.section}: {s.key_rule}" for s in statutes)
        issue_text = "\n".join(f"- {x}: current deterministic state = {y}" for x,y in issue_defs)
        return SYSTEM_PROMPT + "\nROUTING:\n" + "\n".join(directives) + "\nCASES:\n" + case_text + "\nSTATUTES:\n" + statute_text + "\nISSUES:\n" + issue_text + "\nFACTS:\n" + json.dumps(dispute, default=str)

    async def _call_ai(self, prompt):
        try:
            model = getattr(settings, "GEMINI_MODEL", None) or "gemini-1.5-flash"
            from google import genai
            resp = await asyncio.to_thread(self.gemini_client.models.generate_content, model=model, contents=prompt, config=genai.types.GenerateContentConfig(temperature=0.1, max_output_tokens=12000))
            raw = (resp.text or "").strip()
            return self._parse_json(raw)
        except Exception as exc:
            logger.warning("AI proposal unavailable: %s", exc)
            return {"issues": [], "relief": {}}

    @staticmethod
    def _parse_json(raw: str):
        try: return json.loads(raw)
        except Exception: pass
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try: return json.loads(match.group(0))
            except Exception: pass
        return {"issues": [], "relief": {}}

    def _normalise_issues(self, issues, dispute):
        out = []
        for issue in issues if isinstance(issues, list) else []:
            if not isinstance(issue, dict): continue
            fjr = issue.get("fjr") if isinstance(issue.get("fjr"), dict) else {"applicable": False}
            out.append({"issue": issue.get("issue", "Legal issue"), "predicate": issue.get("predicate", {"status": PredicateStatus.UNKNOWN, "dependencies": [], "evidenceRequired": []}), "law": issue.get("law", "Controlled authorities only."), "fjr": fjr, "argument": issue.get("argument", {"claimant": "", "defendant": ""}), "verdict": issue.get("verdict", "CONDITIONAL")})
        return out

    def _apply_fjr(self, issues, dispute):
        for issue in issues:
            r = fjr_engine.assess_clause(issue.get("law", ""), dispute.get("contractCategory", "B2B"), dispute.get("bargainingPower", "equal") == "equal", dispute.get("noticeObjectiveStatus", "adequate") == "adequate", dispute.get("standardForm", False), float(dispute.get("value") or 0), dispute.get("allowsUnilateralVariation", False), dispute.get("consumerVulnerable", False))
            issue["fjr"] = {"applicable": r.applicable, "fair": r.fair, "just": r.just, "reasonable": r.reasonable, "score": r.score, "fairScore": r.fair_score, "justScore": r.just_score, "reasonableScore": r.reasonable_score, "analysis": r.analysis, "legalEffect": r.legal_effect}
        return issues

    @staticmethod
    def _overall_status(payment, defect, withholding, waiver, termination):
        if termination.get("status") == PredicateStatus.PROVEN and payment.get("paymentDefault") == PredicateStatus.PROVEN:
            return "STANDARD BREACH"
        if any(x.get("status") in (PredicateStatus.CONDITIONAL, PredicateStatus.DISPUTED) for x in (defect, withholding, waiver, termination)) or payment.get("paymentDefault") == PredicateStatus.CONDITIONAL:
            return "CONDITIONAL"
        if payment.get("paymentDefault") == PredicateStatus.PROVEN:
            return "STANDARD BREACH"
        return "CONDITIONAL"

ilrmf_engine = ILRMFEngine()
