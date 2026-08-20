"""SAIF controlled case-law corpus v3.1."""
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Case:
    name: str
    citation: str
    key_holding: str
    area: str
    tags: List[str] = field(default_factory=list)
    authority_status: str = "VERIFIED"

PHASE1_CASES = [
    Case("Butler Machine Tool Co Ltd v Ex-Cell-O Corp (England) Ltd", "[1979] 1 WLR 401", "Battle-of-the-forms formation must be analysed from exchanged contractual terms and objective agreement.", "general_contract", ["battle_of_the_forms", "incorporation"]),
    Case("L'Estrange v F Graucob Ltd", "[1934] 2 KB 394", "Signature generally binds a party to the contractual document, subject to recognised exceptions.", "general_contract", ["signature", "incorporation"]),
    Case("Thornton v Shoe Lane Parking Ltd", "[1971] 2 QB 163", "Onerous or unusual terms require sufficient notice to support incorporation.", "general_contract", ["notice", "incorporation"]),
    Case("Interfoto Picture Library Ltd v Stiletto Visual Programmes Ltd", "[1989] QB 433", "Particularly onerous or unusual terms require adequate and prominent notice.", "general_contract", ["notice", "onerous_terms"]),
    Case("Hochster v De La Tour", "(1853) 2 E & B 678", "Unequivocal anticipatory refusal may amount to anticipatory breach.", "general_contract", ["repudiation", "termination"]),
    Case("Hadley v Baxendale", "(1854) 9 Exch 341", "Contract damages are subject to the ordinary remoteness rules and special circumstances framework.", "general_contract", ["damages", "remoteness"]),
    Case("Planche v Colburn", "(1831) 8 Bing 14", "Quantum meruit may arise where contractual work has been performed and the contractual arrangement is abandoned in qualifying circumstances.", "general_contract", ["quantum_meruit"]),
    Case("Photo Production Ltd v Securicor Transport Ltd", "[1980] AC 827", "Exclusion clauses are matters of construction and, where UCTA applies, statutory reasonableness requirements govern.", "b2b_commercial", ["ucta", "exclusion"]),
    Case("Regus (UK) Ltd v Epcot Solutions Ltd", "[2008] EWCA Civ 361", "A commercial limitation may be reasonable depending on the contractual allocation of risk and circumstances.", "b2b_commercial", ["ucta", "limitation"]),
    Case("Tullett Prebon (Services) Ltd v BGC Brokers LP", "[2011] EWCA Civ 131", "Contractual termination rights must be exercised according to the contractual machinery.", "b2b_commercial", ["termination"]),
    Case("Sopar Group (UK) Ltd v Inbiza Retail Ltd", "[2020] EWHC 2354 (Ch)", "Acceptance/rejection must be tested against the contractual specification and agreed scope.", "b2b_commercial", ["acceptance", "software"], "REVIEW_REQUIRED"),
    Case("Bristol Airport plc v Powdrill", "[1990] Ch 744", "Contractual discretion is constrained by the contractual framework and cannot be treated as unlimited.", "b2b_commercial", ["discretion"], "REVIEW_REQUIRED"),
    Case("Robin Ray v Classic FM plc", "[1998] FSR 622", "Copyright ownership and licence rights depend on the contractual and statutory arrangement.", "b2b_commercial", ["copyright", "assignment"], "REVIEW_REQUIRED"),
    Case("Clegg v Andersson (t/a Nordic Marine)", "[2003] EWCA Civ 320", "Sale-of-goods rejection and acceptance depend on the statutory framework and facts of inspection and rejection.", "b2b_commercial", ["sale_of_goods", "rejection"], "REVIEW_REQUIRED"),
    Case("J & H Ritchie Ltd v Lloyd Ltd", "[2007] UKHL 9", "Defective-goods remedies must be analysed within the contractual and statutory remedial framework.", "b2b_commercial", ["sale_of_goods", "defect"], "REVIEW_REQUIRED"),
    Case("Director General of Fair Trading v First National Bank plc", "[2001] UKHL 52", "Consumer unfair-term assessment concerns good faith, significant imbalance and contractual context.", "b2c_consumer", ["consumer", "unfair_terms"]),
    Case("British Home Stores Ltd v Burchell", "[1980] ICR 303", "Traditional misconduct dismissal analysis includes belief, reasonable grounds and investigation.", "employment", ["unfair_dismissal"]),
    Case("Polkey v A E Dayton Services Ltd", "[1988] AC 344", "Procedural failures can affect compensation in unfair-dismissal cases.", "employment", ["procedure"]),
    Case("Wilson v Racher", "[1974] ICR 428", "Constructive dismissal requires repudiatory breach and resignation in response.", "employment", ["constructive_dismissal"]),
    Case("Liverpool City Council v Irwin", "[1977] AC 239", "Terms may be implied where necessary to make a tenancy relationship workable.", "tenancy", ["implied_terms"]),
    Case("Southwark London Borough Council v Mills", "[2001] 1 AC 1", "Housing-condition liability must be analysed against the applicable statutory and contractual framework.", "tenancy", ["disrepair"], "VERIFIED"),
]

def get_cases_by_area(area: str): return [c for c in PHASE1_CASES if c.area.lower() == str(area).lower()]
def get_verified_cases(): return [c for c in PHASE1_CASES if c.authority_status == "VERIFIED"]
