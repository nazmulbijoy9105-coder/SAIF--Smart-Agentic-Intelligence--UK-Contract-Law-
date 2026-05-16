from app.ilrmf.fjr_engine import fjr_engine
from app.validators.citation_checker import citation_checker

def test_fjr_equal_b2b():
    r = fjr_engine.assess_clause("Deliver goods within 30 days.", "B2B", True, True, False, 10000)
    assert r.fair is True

def test_fjr_death_exclusion_b2c():
    r = fjr_engine.assess_clause("Not liable for death or personal injury.", "B2C", False, False, True, 500, consumer_vulnerable=True)
    assert r.reasonable is False

def test_citation_passes():
    r = citation_checker.validate({"issues": [{"law": "Hyde v Wrench [1840]"}]}, 1)
    assert r["passed"] is True
