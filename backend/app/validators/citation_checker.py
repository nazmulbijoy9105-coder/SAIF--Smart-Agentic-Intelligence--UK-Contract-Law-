import re
from typing import Dict, List
from app.corpus.phase1_cases import PHASE1_CASES
from app.corpus.statutes import STATUTES
from app.utils.logger import logger


class CitationChecker:
    def validate(self, result: dict, phase: int = 1) -> Dict:
        verified_cases = [c.name.lower() for c in PHASE1_CASES]
        verified_statutes = [f"{s.act} {s.section}".lower() for s in STATUTES]
        text = self._extract_text(result)
        found = self._extract_citations(text)

        flagged = []
        for c in found:
            c_lower = c.lower()
            matched = False

            # Check against verified cases — both directions + prefix matching
            for v in verified_cases:
                if v == c_lower:
                    matched = True
                    break
                if v in c_lower or c_lower in v:
                    matched = True
                    break
                # Prefix match: "butler machine tool v ex" matches "butler machine tool v ex-cell-o"
                v_parts = v.split()
                c_parts = c_lower.split()
                if len(c_parts) >= 3 and len(v_parts) >= 3:
                    if c_parts[:3] == v_parts[:3]:
                        matched = True
                        break
                    # "X v Y" pattern: match claimant + "v" + first word of defendant
                    if c_parts[0] == v_parts[0] and "v" in c_parts and "v" in v_parts:
                        v_idx = v_parts.index("v")
                        c_idx = c_parts.index("v")
                        if v_idx == c_idx and v_idx + 1 < len(v_parts) and c_idx + 1 < len(c_parts):
                            if v_parts[v_idx + 1].startswith(c_parts[c_idx + 1]):
                                matched = True
                                break

            # Check against verified statutes
            if not matched:
                for s in verified_statutes:
                    if s in c_lower or c_lower in s:
                        matched = True
                        break

            if not matched:
                flagged.append(c)

        passed = len(flagged) == 0
        if not passed:
            logger.warning(f"⚠️ HALLUCINATION FLAGGED: {flagged[:5]}")
        else:
            logger.info(f"✅ All citations verified: {len(found)} found, 0 flagged")

        return {
            "passed": passed,
            "total_found": len(found),
            "verified_count": len(found) - len(flagged),
            "flagged_count": len(flagged),
            "flagged_citations": flagged[:10],
            "phase": phase,
        }

    def _extract_text(self, obj, d=0) -> str:
        if d > 10:
            return ""
        parts = []
        if isinstance(obj, str):
            parts.append(obj)
        elif isinstance(obj, dict):
            for v in obj.values():
                parts.append(self._extract_text(v, d + 1))
        elif isinstance(obj, list):
            for i in obj:
                parts.append(self._extract_text(i, d + 1))
        return " ".join(parts)

    def _extract_citations(self, text: str) -> List[str]:
        citations = set()
        # Pattern 1: Case v Case [year] — e.g., "Butler Machine Tool v Ex-Cell-O [1979]"
        for m in re.finditer(r'[A-Z][a-zA-Z\s]+v\s[A-Z][a-zA-Z\s\-]+?\[\d{4}\]', text):
            citations.add(m.group().strip())
        # Pattern 2: Case v Case (no year) — e.g., "Butler Machine Tool v Ex-Cell-O"
        for m in re.finditer(r'[A-Z][a-zA-Z\s]+v\s[A-Z][a-zA-Z\s\-]+?(?=\s*[,.:;]|\s*$)', text):
            c = m.group().strip()
            # Must have at least "X v Y" structure (3+ parts)
            if len(c.split()) >= 3:
                citations.add(c)
        return list(citations)


citation_checker = CitationChecker()