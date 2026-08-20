"""SAIF ILRMF v3.1 FJR analytical layer."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class FJRResult:
    applicable: bool
    fair: Optional[bool]
    just: Optional[bool]
    reasonable: Optional[bool]
    score: Optional[int]
    fair_score: Optional[int]
    just_score: Optional[int]
    reasonable_score: Optional[int]
    analysis: str
    legal_effect: str = "ANALYTICAL_ONLY"
    verdict: str = "ANALYTICAL_ONLY"

class FJREngine:
    def assess_clause(self, clause: str, contract_type: str, bargaining_power_equal: bool,
                      notice_adequate: bool, standard_form: bool, value_of_contract: float,
                      allows_unilateral_variation: bool = False,
                      consumer_vulnerable: bool = False) -> FJRResult:
        text = str(clause or "").lower()
        cat = str(contract_type or "B2B").upper()
        is_consumer = cat == "B2C"
        relevant = any(k in text for k in ("exclude", "limitation", "limit liability", "cap liability", "penalty", "unilateral variation", "vary")) or allows_unilateral_variation
        if not relevant:
            return FJRResult(False, None, None, None, None, None, None, None,
                             "FJR is not engaged for this issue on the supplied facts.")
        fair, just, reasonable = 50, 50, 50
        fr, jr, rr = [], [], []
        if not bargaining_power_equal:
            fair -= 15; just -= 15; reasonable -= 10
            fr.append("Unequal bargaining power is adverse to fairness.")
            jr.append("Unequal bargaining power is adverse to substantive justice.")
            rr.append("Unequal bargaining power is adverse to reasonableness.")
        if not notice_adequate:
            fair -= 20; just -= 10; reasonable -= 20
            fr.append("Inadequate notice is adverse to procedural fairness.")
            jr.append("Insufficient notice weakens informed assent.")
            rr.append("Inadequate notice is adverse to reasonableness.")
        if standard_form:
            fair -= 5
            fr.append("Standard-form presentation reduces negotiation opportunity.")
        if is_consumer:
            fair -= 10; just -= 10; reasonable -= 15
            fr.append("Consumer status increases fairness scrutiny.")
            jr.append("Consumer context increases substantive imbalance scrutiny.")
            rr.append("Consumer status increases reasonableness scrutiny.")
        if allows_unilateral_variation:
            fair -= 15; just -= 15; reasonable -= 15
            fr.append("Unilateral variation is adverse to fairness.")
            jr.append("Unilateral variation increases imbalance.")
            rr.append("Unilateral variation is adverse to reasonableness.")
        if consumer_vulnerable:
            fair -= 10; just -= 10; reasonable -= 10
        if not bargaining_power_equal is False and cat == "B2B" and value_of_contract > 10000:
            reasonable += 15
            rr.append("Equal commercial bargaining power supports negotiated risk allocation.")
        if not fr: fr.append("No configured adverse fairness factor identified.")
        if not jr: jr.append("No configured adverse justice factor identified.")
        if not rr: rr.append("No configured adverse reasonableness factor identified.")
        fair = max(0, min(100, fair)); just = max(0, min(100, just)); reasonable = max(0, min(100, reasonable))
        score = int(fair * .30 + just * .30 + reasonable * .40)
        return FJRResult(True, fair >= 50, just >= 50, reasonable >= 50, score, fair, just, reasonable,
                         f"FAIR {fair}/100: {'; '.join(fr)}\n\nJUST {just}/100: {'; '.join(jr)}\n\nREASONABLE {reasonable}/100: {'; '.join(rr)}\n\nWEIGHTED SCORE: {score}/100.\n\nLEGAL EFFECT: Analytical only; the applicable legal rule determines enforceability.")

fjr_engine = FJREngine()
