def estimate_monthly_savings(frequency_per_month, manual_minutes, automated_minutes, monthly_cost=0, hourly_labor_cost=0):
    frequency = max(float(frequency_per_month or 0), 0)
    manual = max(float(manual_minutes or 0), 0)
    automated = max(float(automated_minutes or 0), 0)
    cost = max(float(monthly_cost or 0), 0)
    hourly = max(float(hourly_labor_cost or 0), 0)
    hours_saved = max(manual - automated, 0) * frequency / 60
    labor_value = hours_saved * hourly
    return {"hours_saved_monthly": hours_saved, "estimated_labor_value": labor_value,
            "monthly_tool_cost": cost, "estimated_net_monthly_benefit": labor_value - cost}
