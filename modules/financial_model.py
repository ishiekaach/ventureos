import math

def safe_divide(numerator, denominator):
    if numerator is None or denominator in (None, 0): return None
    return numerator / denominator

def revenue_growth(current_revenue, prior_revenue):
    if prior_revenue in (None, 0) or current_revenue is None: return None
    return current_revenue / prior_revenue - 1

def gross_profit(revenue, cogs):
    if revenue is None or cogs is None: return None
    return revenue - cogs

def gross_margin(revenue, cogs):
    return safe_divide(gross_profit(revenue, cogs), revenue)

def ebitda(operating_income, depreciation_amortization):
    if operating_income is None: return None
    return operating_income + (depreciation_amortization or 0)

def ebitda_margin(ebitda_value, revenue):
    return safe_divide(ebitda_value, revenue)

def runway_months(cash_balance, monthly_net_burn):
    if cash_balance is None or monthly_net_burn is None: return None
    if monthly_net_burn <= 0: return math.inf
    return cash_balance / monthly_net_burn

def ownership_after_dilution(initial_ownership, dilution_rounds):
    ownership = initial_ownership
    for dilution in dilution_rounds:
        if not 0 <= dilution < 1: raise ValueError("Each dilution assumption must be between 0% and 100%.")
        ownership *= (1 - dilution)
    return ownership

def vc_return(investment_amount, pre_money, exit_valuation, dilution_rounds=None):
    if investment_amount <= 0 or pre_money < 0 or exit_valuation < 0:
        raise ValueError("Investment must be positive; valuations cannot be negative.")
    post_money = pre_money + investment_amount
    initial_ownership = investment_amount / post_money if post_money else 0
    exit_ownership = ownership_after_dilution(initial_ownership, dilution_rounds or [])
    proceeds = exit_ownership * exit_valuation
    return {"post_money_valuation": post_money, "initial_ownership": initial_ownership,
            "exit_ownership": exit_ownership, "exit_proceeds": proceeds,
            "moic": proceeds / investment_amount}

def irr_from_dates(investment_amount, proceeds, years):
    if investment_amount <= 0 or proceeds < 0 or years <= 0: return None
    return (proceeds / investment_amount) ** (1 / years) - 1

def calculate_comps_multiples(df):
    out = df.copy()
    out["ev_revenue"] = out.apply(lambda r: safe_divide(r.get("enterprise_value"), r.get("revenue")), axis=1)
    out["ev_ebitda"] = out.apply(lambda r: safe_divide(r.get("enterprise_value"), r.get("ebitda")), axis=1)
    return out
