from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class StatuteProvision:
    act: str; year: int; section: str; title: str; applies_to: str; key_rule: str; phase: int = 1

STATUTES: List[StatuteProvision] = [
    StatuteProvision("UCTA 1977", 1977, "s.2(1)", "Death/personal injury exclusion VOID", "Both", "Cannot exclude liability for death/personal injury from negligence."),
    StatuteProvision("UCTA 1977", 1977, "s.2(2)", "Negligence — other loss requires reasonableness", "Both", "Other negligence liability can be excluded only if reasonable."),
    StatuteProvision("UCTA 1977", 1977, "s.3", "Written standard terms", "B2B", "Cannot exclude liability on standard terms unless reasonable."),
    StatuteProvision("UCTA 1977", 1977, "Schedule 2", "Reasonableness guidelines", "B2B", "Factors: bargaining strength, inducement, knowledge, special order, trade custom."),
    StatuteProvision("Consumer Rights Act 2015", 2015, "s.62", "Unfair terms test", "B2C", "Unfair if contrary to good faith and causes significant imbalance."),
    StatuteProvision("Consumer Rights Act 2015", 2015, "Schedule 2", "Grey list indicators", "B2C", "Indicators: exclusion of liability, limiting remedies, unilateral variation."),
    StatuteProvision("Limitation Act 1980", 1980, "s.5", "6-year limitation", "Both", "6 years from date cause of action accrued for simple contract."),
]
