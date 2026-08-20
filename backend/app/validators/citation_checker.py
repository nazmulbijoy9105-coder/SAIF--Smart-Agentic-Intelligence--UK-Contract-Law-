"""SAIF citation/corpus validator v3.1."""
from __future__ import annotations
import re
from typing import Dict, Any
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES

class CitationChecker:
    def __init__(self):
        self.cases = PHASE1_CASES
        self.statutes = STATUTES
    def validate(self, parsed: Dict[str, Any], phase: int) -> dict:
        text = "\n".join(str(i.get("law", "")) for i in parsed.get("issues", []) if isinstance(i, dict))
        violations, warnings = [], []
        for c in self.cases:
            if c.name.lower() in text.lower() or c.citation.lower() in text.lower():
                if c.authority_status != "VERIFIED": warnings.append(f"Review-required authority: {c.name} {c.citation}")
        bracketed = set(re.findall(r"\[\d{4}\](?:\s+[A-Z][A-Za-z0-9.() -]+)?", text))
        allowed = {c.citation for c in self.cases}
        for cit in bracketed:
            if not any(cit.strip() == a or cit.strip() in a or a in cit.strip() for a in allowed):
                violations.append(f"Unverified citation: {cit.strip()}")
        return {"passed": not violations, "phase": phase, "violations": violations, "warnings": warnings, "status": "PASSED" if not violations else "FAILED", "checked_at": "citation_checker_v3.1"}

citation_checker = CitationChecker()
