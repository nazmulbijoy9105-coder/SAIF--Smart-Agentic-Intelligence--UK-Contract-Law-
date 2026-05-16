import re
from typing import Dict, List
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES
from app.utils.logger import logger

class CitationChecker:
    def validate(self, result: dict, phase: int = 1) -> Dict:
        verified_cases = {c.name.lower() for c in PHASE1_CASES}
        verified_statutes = {f"{s.act} {s.section}".lower() for s in STATUTES}
        text = self._extract_text(result)
        found = self._extract_citations(text)
        flagged = [c for c in found if not any(v in c.lower() for v in verified_cases | verified_statutes)]
        passed = len(flagged) == 0
        if not passed: logger.warning(f"⚠️ HALLUCINATION FLAGGED: {flagged[:5]}")
        return {"passed": passed, "total_found": len(found), "flagged_count": len(flagged), "flagged_citations": flagged[:10], "phase": phase}

    def _extract_text(self, obj, d=0) -> str:
        if d > 10: return ""
        parts = []
        if isinstance(obj, str): parts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values(): parts.append(self._extract_text(v, d+1))
        elif isinstance(obj, list):
            for i in obj: parts.append(self._extract_text(i, d+1))
        return " ".join(parts)

    def _extract_citations(self, text: str) -> List[str]:
        citations = set()
        for p in [r'[A-Z][a-zA-Z\s]+v\s[A-Z][a-zA-Z\s]+\[\d{4}\]', r'[A-Z][a-zA-Z\s]+v\s[A-Z][a-zA-Z]+']:
            for m in re.finditer(p, text): citations.add(m.group().strip())
        return list(citations)

citation_checker = CitationChecker()
