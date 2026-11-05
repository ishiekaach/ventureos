def money(value, decimals=1):
    if value is None: return "N/A"
    sign = "-" if value < 0 else ""
    value = abs(float(value))
    if value >= 1_000_000_000: return f"{sign}${value/1_000_000_000:,.{decimals}f}B"
    if value >= 1_000_000: return f"{sign}${value/1_000_000:,.{decimals}f}M"
    if value >= 1_000: return f"{sign}${value/1_000:,.{decimals}f}K"
    return f"{sign}${value:,.0f}"

def pct(value, decimals=1):
    return "N/A" if value is None else f"{value:.{decimals}%}"
