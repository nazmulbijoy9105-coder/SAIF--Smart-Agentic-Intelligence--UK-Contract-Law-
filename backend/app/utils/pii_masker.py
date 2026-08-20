"""SAIF PII input sanitiser v3.1."""
from __future__ import annotations
import copy, re
from typing import Any, Dict, Tuple

class _PIIMasker:
    EMAIL = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b")
    PHONE = re.compile(r"(?<!\d)(?:\+44|0)\d{3,4}[\s.\-]?\d{3,4}[\s.\-]?\d{3,6}(?!\d)")
    POSTCODE = re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b", re.I)
    NAME = re.compile(r"\b(?:Mr|Mrs|Ms|Miss|Dr|Prof)\.?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b")
    def mask_dispute(self, dispute: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        mapping = {}; counters = {"EMAIL":0,"PHONE":0,"POSTCODE":0,"PERSON":0}
        def walk(obj):
            if isinstance(obj, dict): return {k: walk(v) for k,v in obj.items()}
            if isinstance(obj, list): return [walk(v) for v in obj]
            if isinstance(obj, str): return self._mask(obj, mapping, counters)
            return obj
        return walk(copy.deepcopy(dispute)), mapping
    def _mask(self, text, mapping, counters):
        for label, pattern in (("EMAIL",self.EMAIL),("PHONE",self.PHONE),("POSTCODE",self.POSTCODE),("PERSON",self.NAME)):
            def repl(m, label=label):
                counters[label]+=1; tok=f"<<{label}_{counters[label]:04d}>>"; mapping[tok]=m.group(0); return tok
            text = pattern.sub(repl, text)
        return text
    def unmask_response(self, response: Any, mapping: Dict[str,str]) -> Any:
        def walk(obj):
            if isinstance(obj, dict): return {k:walk(v) for k,v in obj.items()}
            if isinstance(obj, list): return [walk(v) for v in obj]
            if isinstance(obj, str):
                for token, original in mapping.items(): obj=obj.replace(token, original)
            return obj
        return walk(response)

PIIMasker = _PIIMasker()
