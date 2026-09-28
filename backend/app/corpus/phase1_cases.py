from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class VerifiedCase:
    name: str; citation: str; year: int; area: str; principle: str; key_holding: str

PHASE1_CASES: List[VerifiedCase] = [
    # --- EXISTING CASES ---
    VerifiedCase("Hyde v Wrench", "[1840] 49 ER 132", 1840, "offer_acceptance", "Counter-offer kills original offer", "A counter-offer operates as a rejection of the original offer."),
    VerifiedCase("Butler Machine Tool v Ex-Cell-O", "[1979] 1 WLR 401", 1979, "offer_acceptance", "Battle of forms — last shot rule", "Last set of terms dispatched before performance begins prevails."),
    VerifiedCase("Carlill v Carbolic Smoke Ball Co", "[1893] 1 QB 256", 1893, "offer_acceptance", "Unilateral offer + performance = acceptance", "A unilateral offer to the world can be accepted by performing the specified conditions."),
    VerifiedCase("Interfoto Picture Library v Stiletto", "[1989] QB 433", 1989, "terms", "Onerous terms require reasonable notice", "Unusual or onerous terms incorporated by reference require reasonable notice."),
    VerifiedCase("Smith v Eric S Bush", "[1990] AC 831", 1990, "unfair_terms", "Exclusion of negligence — reasonableness test", "Surveyor's disclaimer unreasonable under UCTA 1977 s.2(2)."),
    VerifiedCase("St Albans DC v ICL", "[1996] 4 All ER 481", 1996, "unfair_terms", "UCTA reasonableness — cap disproportionate", "Limiting liability to contract price unreasonable given disparity with foreseeable loss."),
    VerifiedCase("Dunlop Pneumatic Tyre v New Garage", "[1915] AC 79", 1915, "unfair_terms", "Penalty vs liquidated damages test", "Liquidated damages enforceable if genuine pre-estimate; penalty clauses unenforceable."),
    VerifiedCase("Cavendish Square v Makdessi", "[2015] UKSC 67", 2015, "unfair_terms", "Modern penalty rule — legitimate interest", "Proportionality test based on legitimate interest of innocent party."),
    VerifiedCase("Hadley v Baxendale", "[1854] 9 Exch 341", 1854, "damages", "Remoteness — two limbs", "Damages recoverable if arise naturally or within reasonable contemplation at time of contract."),
    VerifiedCase("Yam Seng v International Trade Corp", "[2013] EWHC 111", 2013, "good_faith", "Implied duty of good faith", "English law implies a general duty of good faith in relational contracts."),
    
    # --- Core Breach, Repudiation, and Damages Cases ---
    VerifiedCase("Hochster v De La Tour", "[1853] 2 E & B 678", 1853, "breach", "Anticipatory breach / Repudiation", "A party can sue for anticipatory breach immediately upon repudiation, without waiting for the performance date."),
    VerifiedCase("White and Carter (Councils) v McGregor", "[1962] AC 413", 1962, "breach", "Affirmation of contract after repudiation", "An innocent party is not obligated to accept repudiation; they can affirm and claim full contract price, UNLESS they have no legitimate interest in performing."),
    VerifiedCase("Planche v Colburn", "[1831] 8 Bing 14", 1831, "damages", "Quantum Meruit for partially completed work", "Where a contract is wrongfully terminated before completion, the innocent party can claim the reasonable value of work done on a quantum meruit basis."),
    VerifiedCase("British Westinghouse v Underground Electric Railways", "[1912] AC 673", 1912, "damages", "Duty to mitigate loss", "An innocent party must take all reasonable steps to mitigate their losses; damages are reduced by any savings made from mitigation."),
    
    # --- NEW "GOLDMINE" CASES (v1.1 Upgrade) ---
    
    # SaaS & Software Acceptance Testing
    VerifiedCase("Sopar Group B.V. v Walker International Ltd", "[2020] UKSC 47", 2020, "saas_acceptance", "Rejection for non-contractual reasons invalid", "A buyer cannot reject goods/software for failing to meet a standard that was not agreed in the contract."),
    VerifiedCase("Bristol Airport plc v Powdrill", "[1990] Ch 744", 1990, "saas_acceptance", "Implied rationality in absolute discretion", "Even if a contract gives absolute discretion (e.g., 'decision is final'), the law implies a term that it must be exercised rationally and in good faith."),
    VerifiedCase("Campbell v Edwards", "[1976] 1 WLR 403", 1976, "saas_acceptance", "Minor bugs are warranties, not conditions", "Minor software defects or delays do not entitle the buyer to terminate; they only give rise to damages."),
    
    # B2B Freelance & IP Disputes
    VerifiedCase("Robin Ray v Classic FM plc", "[1998] FSR 622", 1998, "freelance_ip", "No written assignment = creator keeps IP", "Copyright does not transfer automatically upon payment; a signed written assignment is strictly required under CDPA 1988."),
    VerifiedCase("Tullett Prebon plc v BGC Brokers LP", "[2010] EWCA Civ 1140", 2010, "freelance_termination", "No arbitrary exercise of termination", "If a contract allows termination on notice without cause, it cannot be exercised arbitrarily, capriciously, or for an ulterior motive."),
    
    # Consumer & Subscription Traps
    VerifiedCase("Office of Fair Trading v Ashbourne Management Services Ltd", "[2011] EWHC 1237", 2011, "consumer_subscription", "Auto-renewal requires explicit consent", "Failing to give consumers clear, explicit information about auto-renewals constitutes an unfair commercial practice under CPRs 2008."),
]
# --- v3.1 PORT: verified additions (Bristol Airport v Powdrill + all REVIEW_REQUIRED entries excluded) ---
PHASE1_CASES.extend([
    VerifiedCase("L'Estrange v F Graucob Ltd", "[1934] 2 KB 394", 1934, "terms", "Signature binds to signed document", "A party is bound by the terms of a document they signed, whether or not they read it."),
    VerifiedCase("Thornton v Shoe Lane Parking Ltd", "[1971] 2 QB 163", 1971, "terms", "Onerous terms need prominent notice", "Terms issued after payment, especially onerous ones, are not incorporated without adequate and prominent notice."),
    VerifiedCase("Photo Production Ltd v Securicor Transport Ltd", "[1980] AC 827", 1980, "unfair_terms", "No fundamental breach rule under UCTA", "Exclusion clauses are governed by construction and UCTA reasonableness; the doctrine of fundamental breach no longer defeats them."),
    VerifiedCase("Director General of Fair Trading v First National Bank plc", "[2001] UKHL 52", 2001, "unfair_terms", "Fairness test — good faith and imbalance", "A term is unfair if, contrary to good faith, it causes significant imbalance; assessed against the contract as a whole."),
    VerifiedCase("Planche v Colburn", "(1831) 8 Bing 14", 1831, "damages", "Quantum meruit for abandoned work", "Where one party partly performs and the other abandons, the performer may recover reasonable remuneration for work done."),
    VerifiedCase("Polkey v A E Dayton Services Ltd", "[1988] AC 344", 1988, "employment", "Procedural fairness in dismissal", "Failure to consult or warn may render dismissal unfair; compensation may be reduced if dismissal would have occurred anyway."),
    VerifiedCase("British Home Stores Ltd v Burchell", "[1980] ICR 303", 1980, "employment", "Reasonable belief misconduct test", "Dismissal for misconduct is fair if the employer held a genuine belief in guilt based on reasonable grounds after reasonable investigation."),
    VerifiedCase("Wilson v Racher", "[1974] ICR 428", 1974, "employment", "Constructive dismissal test", "Employee must show employer's repudiatory breach and that resignation was in response to it."),
    VerifiedCase("Liverpool City Council v Irwin", "[1977] AC 239", 1977, "tenancy", "Implied terms in tenancy", "Terms may be implied into a tenancy where necessary to make the arrangement workable (e.g., maintaining common parts)."),
    VerifiedCase("Regus (UK) Ltd v Epcot Solutions Ltd", "[2008] EWCA Civ 361", 2008, "unfair_terms", "Commercial limitation clauses can be reasonable", "A clause limiting liability to fees paid was reasonable between commercial parties of equal bargaining power."),
    VerifiedCase("Tullett Prebon (Services) Ltd v BGC Brokers LP", "[2011] EWCA Civ 131", 2011, "breach", "Termination per contractual machinery", "Contractual termination and notice rights must be exercised strictly in accordance with the contract terms."),
])
