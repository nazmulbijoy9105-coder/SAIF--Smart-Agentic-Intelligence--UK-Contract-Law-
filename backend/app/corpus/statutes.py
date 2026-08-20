"""SAIF controlled statutory corpus v3.1."""
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Statute:
    act: str
    section: str
    key_rule: str
    applies_to: str
    tags: List[str] = field(default_factory=list)
    authority_status: str = "VERIFIED"

STATUTES = [
    Statute("Unfair Contract Terms Act 1977", "s.2(1)", "Liability for death or personal injury resulting from negligence cannot be excluded or restricted where the section applies.", "Both", ["ucta", "personal_injury"]),
    Statute("Unfair Contract Terms Act 1977", "s.3", "Where the statutory gateway is satisfied, exclusion/restriction of contractual liability is subject to reasonableness.", "Both", ["ucta", "reasonableness"]),
    Statute("Unfair Contract Terms Act 1977", "s.11", "Where UCTA imposes reasonableness, the term must be fair and reasonable in the circumstances contemplated at formation.", "Both", ["ucta", "reasonableness"]),
    Statute("Unfair Contract Terms Act 1977", "Schedule 2", "Guidelines include bargaining strength, knowledge of the term and practicability of compliance.", "Both", ["ucta", "bargaining_power"]),
    Statute("Sale of Goods Act 1979", "s.14", "Where applicable, business-sale goods must satisfy statutory requirements concerning satisfactory quality and fitness.", "B2B", ["sale_of_goods", "quality", "fitness"]),
    Statute("Sale of Goods Act 1979", "s.15A", "In a non-consumer sale, a sufficiently slight breach may affect the buyer's rejection right where rejection would be unreasonable, subject to the statutory conditions.", "B2B", ["sale_of_goods", "rejection"]),
    Statute("Sale of Goods Act 1979", "s.53", "For breach of warranty, the buyer may set up diminution or extinction of price or claim damages, subject to the statutory measure.", "B2B", ["sale_of_goods", "price", "damages"]),
    Statute("Late Payment of Commercial Debts (Interest) Act 1998", "s.1-s.5", "The statutory scheme may imply interest and compensation for qualifying late commercial debts; rate and period must be determined for the relevant period.", "B2B", ["late_payment", "interest"]),
    Statute("Consumer Rights Act 2015", "ss.9-11", "Consumer goods must meet statutory standards including satisfactory quality, fitness and description.", "B2C", ["consumer", "goods"]),
    Statute("Consumer Rights Act 2015", "ss.19-24", "Consumer remedies for non-conforming goods include the statutory rejection, repair/replacement and price-reduction mechanisms, subject to conditions.", "B2C", ["consumer", "remedies"]),
    Statute("Consumer Rights Act 2015", "ss.49-50", "Consumer services must be performed with reasonable care and skill and in accordance with the applicable statutory framework.", "B2C", ["consumer", "services"]),
    Statute("Consumer Rights Act 2015", "s.62", "An unfair consumer term is not binding on the consumer, subject to the statutory fairness test.", "B2C", ["consumer", "unfair_terms"]),
    Statute("Employment Rights Act 1996", "s.98", "Unfair dismissal analysis requires the employer to establish the potentially fair reason and the statutory fairness framework.", "Employment", ["employment"]),
    Statute("Employment Rights Act 1996", "s.123", "Compensation for unfair dismissal is subject to the statutory calculation and applicable current cap.", "Employment", ["employment", "compensation"]),
    Statute("Equality Act 2010", "ss.13, 19, 26", "The Act prohibits specified direct discrimination, indirect discrimination and harassment, subject to statutory elements.", "Employment", ["discrimination"]),
    Statute("Landlord and Tenant Act 1985", "s.11", "Relevant residential tenancies include statutory repairing obligations within the scope of the section.", "Tenancy", ["repair"]),
    Statute("Housing Act 2004", "ss.213-215", "Where applicable, tenancy deposits are subject to statutory protection requirements and remedies.", "Tenancy", ["deposit"]),
    Statute("Senior Courts Act 1981", "s.35A", "The court has power to award simple interest in appropriate cases; rate and period are determined rather than assumed.", "Both", ["interest"]),
]

def get_statutes_by_domain(domain: str): return [s for s in STATUTES if s.applies_to.lower() == str(domain).lower() or s.applies_to == "Both"]
def get_verified_statutes(): return [s for s in STATUTES if s.authority_status == "VERIFIED"]
