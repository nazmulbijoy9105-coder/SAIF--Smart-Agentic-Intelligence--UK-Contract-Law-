class IncorporationGate:
    @staticmethod
    def evaluate(facts):
        score = 50
        reasons = []
        
        if facts.get('rushedSignature'):
            score -= 20
            reasons.append("Pressure to sign quickly weakens implied notice.")
        if not facts.get('specificNotice'):
            score -= 25
            reasons.append("No specific notice of onerous term given.")
        if facts.get('buriedClause'):
            score -= 15
            reasons.append("Clause buried in document, not prominent (Thornton v Shoe Lane).")
        if facts.get('signedDocument'):
            score += 30
            reasons.append("Document signed (L'Estrange v Graucob baseline).")

        incorporated = score >= 50 and not facts.get('buriedClause', False)
        return {"incorporated": incorporated, "score": score, "reasons": reasons}


class FJRDynamicScorer:
    @staticmethod
    def score(issue, facts):
        fair, just, reasonable = 50, 50, 50

        if facts.get('bargaining') == 'claimant_weaker':
            fair -= 20; just -= 15; reasonable -= 20
        if not facts.get('specificNotice'):
            fair -= 15; reasonable -= 20
        if facts.get('isConsumer'):
            just -= 15; reasonable -= 15
            
        # UCTA s.2(1) personal injury absolute bar
        if 's.2(1)' in issue.get('law', ''):
            reasonable = 0
            
        # Unfair variation (CRA Sch.2 Para 4)
        if 'Unilateral Variation' in issue.get('law', '') or 'variation' in issue.get('description', '').lower():
            fair -= 30; just -= 30

        return {
            "fair": max(0, min(100, fair)),
            "just": max(0, min(100, just)),
            "reasonable": max(0, min(100, reasonable)),
            "total": (fair + just + reasonable) / 3
        }


class ProbabilityCalibrator:
    @staticmethod
    def calculate(verdict, issues, facts):
        if verdict != 'VOID':
            return {"probability": 15, "confidence": "Low", "explanation": "Clause deemed valid/enforceable."}

        base_probability = 65
        reasons = ["Base probability 65% due to VOID verdict."]

        has_personal_injury = any('s.2(1)' in i.get('law', '') for i in issues)
        if has_personal_injury:
            base_probability = 95
            reasons.append("UCTA s.2(1) absolute bar on personal injury exclusion.")
        
        if facts.get('isConsumer'):
            base_probability += 10
            reasons.append("CRA 2015 consumer-friendly bias applied.")
            
        if not facts.get('incorporated', True):
            base_probability += 5
            reasons.append("Incorporation failure strengthens claimant position.")

        if facts.get('evidenceQuality') == 'weak':
            base_probability -= 15
            reasons.append("Weak evidence quality reduces certainty.")

        final_probability = max(5, min(95, base_probability))
        return {"probability": final_probability, "confidence": "High" if final_probability > 70 else "Moderate", "explanation": " ".join(reasons)}


class CourtAssigner:
    @staticmethod
    def assign(claim_value):
        try:
            value = float(claim_value)
        except (ValueError, TypeError):
            return {"track": "N/A", "court": "N/A"}
            
        if value <= 10000:
            return {"track": "Small Claims Track", "court": "County Court"}
        elif value <= 25000:
            return {"track": "Fast Track", "court": "County Court"}
        elif value <= 100000:
            return {"track": "Intermediate Track", "court": "County Court"}
        return {"track": "Multi-Track", "court": "County Court / High Court"}


class ReliefGenerator:
    @staticmethod
    def generate(verdict, facts):
        claim_value = facts.get('claimValue', 'TBD')
        if verdict != 'VOID':
            return {"primary": "N/A", "secondary": "N/A", "damages": claim_value}
            
        return {
            "primary": "Declaration that clause is void and unenforceable",
            "secondary": "Damages for breach of contract / negligence",
            "damages": claim_value,
            "interest": "Statutory interest under Senior Courts Act 1981 s.35A"
        }

# ORCHESTRATOR
class ILRMFPipelineV2:
    @staticmethod
    def run(facts, issues):
        # 1. Incorporation
        incorporation = IncorporationGate.evaluate(facts)
        
        verdict = 'VALID'
        scored_issues = []
        
        if incorporation['incorporated']:
            for issue in issues:
                scores = FJRDynamicScorer.score(issue, facts)
                is_void = scores['fair'] < 50 or scores['just'] < 50 or scores['reasonable'] < 50
                scored_issues.append({**issue, "scores": scores, "verdict": "VOID" if is_void else "VALID"})
            
            if any(i['verdict'] == 'VOID' for i in scored_issues):
                verdict = 'VOID'
        else:
            verdict = 'NOT INCORPORATED'
            
        # 2. Downstream
        facts['incorporated'] = incorporation['incorporated']
        probability = ProbabilityCalibrator.calculate(verdict, scored_issues, facts)
        court = CourtAssigner.assign(facts.get('claimValue', 0))
        relief = ReliefGenerator.generate(verdict, facts)
        
        return {
            "incorporation": incorporation,
            "issues": scored_issues,
            "verdict": verdict,
            "probability": probability,
            "court": court,
            "relief": relief
        }