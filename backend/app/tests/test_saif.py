from app.ilrmf.engine import (
    PredicateStatus, PaymentPredicateEngine, DefectPredicateEngine,
    WithholdingPredicateEngine, WaiverAffirmationEngine,
    TerminationPredicateEngine, DependencyEngine, DisputeRouter,
    IncorporationGate, CourtAssigner,
)
from app.ilrmf.fjr_engine import fjr_engine

def test_fjr_is_analytical_only():
    r=fjr_engine.assess_clause("Supplier may vary price unilaterally", "B2C", False, False, True, 500, True, True)
    assert r.applicable is True
    assert r.legal_effect == "ANALYTICAL_ONLY"
    assert r.score is not None

def test_payment_withheld_is_conditional():
    r=PaymentPredicateEngine.evaluate({"payment":{"invoiceAmount":50000,"amountPaid":38000,"amountWithheld":12000}})
    assert r["paymentDefault"] == PredicateStatus.CONDITIONAL
    assert r["amountDue"] == 12000

def test_defect_allegation_is_not_proof():
    r=DefectPredicateEngine.evaluate({"defect":{"alleged":True,"defectiveUnits":6,"totalUnits":25}})
    assert r["status"] == PredicateStatus.DISPUTED
    assert r["breachStatus"] == PredicateStatus.NOT_PROVEN
    assert r["defectPercentage"] == 24.0

def test_alpha_termination_is_conditional_when_dependencies_unresolved():
    p=PaymentPredicateEngine.evaluate({"payment":{"invoiceAmount":50000,"amountPaid":38000,"amountWithheld":12000}})
    d=DefectPredicateEngine.evaluate({"defect":{"alleged":True,"defectiveUnits":6,"totalUnits":25}})
    w=WithholdingPredicateEngine.evaluate({"payment":{"amountWithheld":12000}},p,d)
    wa=WaiverAffirmationEngine.evaluate({"termination":{"continuedPerformanceAfterBreach":True,"reservationOfRights":None}})
    t=TerminationPredicateEngine.evaluate({"termination":{"clauseExists":True,"noticeDate":"2026-04-20","noticeReceivedDate":"2026-04-20","curePeriodDays":14,"terminationDate":"2026-05-08"}},p,wa,w)
    assert p["paymentDefault"] == PredicateStatus.CONDITIONAL
    assert d["status"] == PredicateStatus.DISPUTED
    assert w["status"] == PredicateStatus.CONDITIONAL
    assert t["status"] == PredicateStatus.CONDITIONAL

def test_dependency_graph():
    graph=DependencyEngine.build({"paymentDefault":PredicateStatus.CONDITIONAL},{"status":PredicateStatus.DISPUTED},{"status":PredicateStatus.CONDITIONAL},{"status":PredicateStatus.CONDITIONAL},{"status":PredicateStatus.CONDITIONAL},{"status":PredicateStatus.UNKNOWN})
    names={x["predicate"] for x in graph}
    assert {"PAYMENT_DEFAULT","DEFECT","WITHHOLDING_RIGHT","TERMINATION_VALID"}.issubset(names)

def test_router_b2b_goods():
    ds=DisputeRouter.route({"contractCategory":"B2B","contractType":"Commercial","summary":"6 compressors defective and £12000 withheld","disputedClause":"Time for payment shall be of the essence."})
    assert any("B2B COMMERCIAL" in x for x in ds)
    assert any("PAYMENT / DEBT" in x for x in ds)
    assert any("GOODS QUALITY" in x for x in ds)

def test_incorporation_conditional():
    r=IncorporationGate.evaluate({"disputedClause":"Exclusion of all liability","signedDocument":False,"unusualOrOnerousTerm":True,"notice_objective_status":"buried"})
    assert r["status"] == "CONDITIONAL"
    assert r["incorporated"] is None

def test_court_assignment():
    assert CourtAssigner.assign(5000,"Commercial")["track"] == "SMALL CLAIMS CANDIDATE"
