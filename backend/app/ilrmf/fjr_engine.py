from dataclasses import dataclass, field
from typing import Optional, List, Dict
import re

@dataclass
class FJRResult:
    fair: bool; just: bool; reasonable: bool; score: int; verdict: str; analysis: str
    ucta_factors: Dict[str, bool] = field(default_factory=dict)
    cra_factors: Dict[str, bool] = field(default_factory=dict)
    fair_score: int = 0; just_score: int = 0; reasonable_score: int = 0

class FJREngine:
    def assess_clause(self, clause: str, contract_type: str, bargaining_power_equal: bool, notice_adequate: bool, standard_form: bool, value_of_contract: float, cap_value: Optional[float] = None, allows_unilateral_variation: bool = False, consumer_vulnerable: bool = False) -> FJRResult:
        indicators = self._analyze_clause(clause or "")
        
        # FAIR GATE
        fs = 0
        if bargaining_power_equal: fs += 30
        if notice_adequate: fs += 25
        if not allows_unilateral_variation: fs += 25
        if not consumer_vulnerable: fs += 20
        if indicators.get("penalty_clause"): fs -= 15
        fs = max(0, min(100, fs))
        fair = fs >= 60

        # JUST GATE
        js = 0
        if bargaining_power_equal: js += 33
        if not allows_unilateral_variation: js += 34
        if not standard_form or notice_adequate: js += 33
        if indicators.get("exclusion_clause"): js -= 10
        js = max(0, min(100, js))
        just = js >= 60

        # REASONABLE GATE
        ucta_factors, cra_factors = {}, {}
        if contract_type == "B2C":
            rs = 100
            if allows_unilateral_variation: rs -= 25
            if not notice_adequate: rs -= 25
            if consumer_vulnerable: rs -= 20
            if indicators.get("excludes_death_injury"): rs = 0
            rs = max(0, min(100, rs))
        else:
            rs = 0
            ucta_factors["bargaining_strength_equal"] = bargaining_power_equal
            if bargaining_power_equal: rs += 30
            ucta_factors["adequate_notice"] = notice_adequate
            if notice_adequate: rs += 30
            ucta_factors["not_standard_form"] = not standard_form
            if not standard_form: rs += 20
            if not allows_unilateral_variation: rs += 20
            if cap_value and value_of_contract > 0 and (cap_value / value_of_contract) < 0.1: rs = min(rs, 20)
            rs = max(0, min(100, rs))
        reasonable = rs >= 60

        combined = max(0, min(100, int(fs * 0.30 + js * 0.30 + rs * 0.40)))
        gates = sum([fair, just, reasonable])
        if gates == 3: verdict = "TERM ENFORCEABLE — all FJR gates passed"
        elif gates == 0: verdict = "TERM VOID — fails all FJR gates"
        elif gates == 1: verdict = "TERM LIKELY VOID — majority FJR failure"
        else: verdict = "TERM AT RISK — partial FJR failure"
        
        analysis = f"FAIR ({fs}/100) | JUST ({js}/100) | REASONABLE ({rs}/100)"
        return FJRResult(fair=fair, just=just, reasonable=reasonable, score=combined, verdict=verdict, analysis=analysis, ucta_factors=ucta_factors, cra_factors=cra_factors, fair_score=fs, just_score=js, reasonable_score=rs)

    def _analyze_clause(self, clause: str) -> dict:
        cl = clause.lower()
        ind = {}
        exclusion_pats = [r'not\s+be\s+liable', r'exclude[s]?\s+.*liability', r'liability\s+is\s+limited']
        ind["exclusion_clause"] = any(re.search(p, cl) for p in exclusion_pats)
        ind["penalty_clause"] = bool(re.search(r'penalty\s+(fee|charge)', cl))
        ind["excludes_death_injury"] = bool(re.search(r'death\s+or\s+personal\s+injury', cl)) and ind["exclusion_clause"]
        return ind

fjr_engine = FJREngine()
