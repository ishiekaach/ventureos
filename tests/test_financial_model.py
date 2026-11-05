import pytest
from modules.financial_model import revenue_growth, gross_margin, ebitda, ebitda_margin, runway_months, vc_return, irr_from_dates, ownership_after_dilution

def test_revenue_growth():
    assert revenue_growth(150,100) == pytest.approx(.5)
    assert revenue_growth(100,0) is None

def test_margins_and_ebitda():
    assert gross_margin(100,40) == pytest.approx(.6)
    assert ebitda(-10,3) == -7
    assert ebitda_margin(20,100) == pytest.approx(.2)

def test_runway():
    assert runway_months(600,100) == pytest.approx(6)
    assert runway_months(600,0) == float("inf")

def test_vc_return():
    r=vc_return(2000000,8000000,100000000,[.30])
    assert r["initial_ownership"] == pytest.approx(.2)
    assert r["exit_ownership"] == pytest.approx(.14)
    assert r["exit_proceeds"] == pytest.approx(14000000)
    assert r["moic"] == pytest.approx(7)

def test_multiple_dilution_rounds():
    assert ownership_after_dilution(.2,[.1,.2]) == pytest.approx(.144)

def test_irr():
    assert irr_from_dates(100,200,5) == pytest.approx(2**.2-1)
