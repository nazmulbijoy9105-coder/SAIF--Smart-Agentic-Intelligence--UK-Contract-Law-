from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class StatuteProvision:
    act: str; year: int; section: str; title: str; applies_to: str; key_rule: str; phase: int = 1

STATUTES: List[StatuteProvision] = [
    # --- EXISTING STATUTES ---
    StatuteProvision("UCTA 1977", 1977, "s.2(1)", "Death/personal injury exclusion VOID", "Both", "Cannot exclude liability for death/personal injury from negligence."),
    StatuteProvision("UCTA 1977", 1977, "s.2(2)", "Negligence — other loss requires reasonableness", "Both", "Other negligence liability can be excluded only if reasonable."),
    StatuteProvision("UCTA 1977", 1977, "s.3", "Written standard terms", "B2B", "Cannot exclude liability on standard terms unless reasonable."),
    StatuteProvision("UCTA 1977", 1977, "Schedule 2", "Reasonableness guidelines", "B2B", "Factors: bargaining strength, inducement, knowledge, special order, trade custom."),
    StatuteProvision("Consumer Rights Act 2015", 2015, "s.62", "Unfair terms test", "B2C", "Unfair if contrary to good faith and causes significant imbalance."),
    StatuteProvision("Consumer Rights Act 2015", 2015, "Schedule 2", "Grey list indicators", "B2C", "Indicators: exclusion of liability, limiting remedies, unilateral variation."),
    StatuteProvision("Limitation Act 1980", 1980, "s.5", "6-year limitation", "Both", "6 years from date cause of action accrued for simple contract."),
    
    # --- NEW "GOLDMINE" STATUTES (v1.1 Upgrade) ---
    StatuteProvision("Late Payment of Commercial Debts (Interest) Act 1998", 1998, "s.2 & s.5", "Statutory Interest for B2B", "B2B", "Entitles supplier to 8% above Bank of England base rate on late invoices, plus fixed £40-£100 recovery costs."),
    StatuteProvision("Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013", 2013, "Reg 13 & 14", "Negative option billing ban", "B2C", "Auto-renewals and 'free trial' traps that require consumer opt-out are automatically unfair."),
    StatuteProvision("Copyright, Designs and Patents Act 1988", 1988, "s.90 & s.91", "IP Assignment requirements", "Both", "Copyright ownership only transfers via signed written document; payment alone does not transfer rights."),
]