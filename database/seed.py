from database.db import execute, query_df

COMPANIES = [
    ("Northstar Workflow AI","Enterprise Software","Seed","San Francisco, CA","B2B SaaS","AI workflow orchestration for operations teams."),
    ("Lumen Robotics","Hardware","Pre-seed","Oakland, CA","Robotics-as-a-Service","Autonomous inspection robotics for industrial facilities."),
    ("LedgerLeaf","Fintech","Series A","New York, NY","B2B SaaS","Financial operations software for growing businesses."),
    ("CarePath Systems","Healthcare","Seed","San Jose, CA","B2B SaaS","Workflow tools for outpatient care coordination."),
    ("CarbonCurrent","Climate Tech","Pre-seed","Denver, CO","Usage-based","Monitoring software for industrial energy efficiency.")
]
AGENTS = [
    ("Company Research Agent","Summarizes company profiles, products, business models, and public research.","Company Research","Company URL and notes","Company summary and key facts",80,18,35,5),
    ("Competitor Mapping Agent","Compares products, target customers, positioning, and differentiation.","Market Research","Company profile and market","Competitor landscape",45,12,50,8),
    ("Research Brief Generator","Creates concise company and industry research briefs from supplied links and notes.","Company Research","Company links and notes","Research brief",40,11,45,7)
]

def seed():
    if not query_df("SELECT company_id FROM companies LIMIT 1").empty: return
    for i, row in enumerate(COMPANIES):
        cid = execute("INSERT INTO companies(name,industry,stage,location,business_model,description,source_type,pipeline_status) VALUES(?,?,?,?,?,?,'Illustrative',?)", (*row, ["New","Initial Screening","Under Evaluation","Due Diligence","New"][i]))
        revenue = [1200000,600000,4500000,1800000,350000][i]
        execute("INSERT INTO financial_metrics(company_id,period,revenue,cogs,operating_income,depreciation_amortization,cash_balance,monthly_net_burn,customer_count,source_type) VALUES(?,?,?,?,?,?,?,?,?,'Illustrative')", (cid,"FY2025",revenue,revenue*.35,-revenue*.18,revenue*.03,revenue*.65,revenue*.025,20+i*13))
    for row in AGENTS:
        name, description, category, inputs, outputs, frequency, cost, manual, automated = row
        execute("INSERT INTO agents(name,description,category,inputs,outputs,frequency_per_month,monthly_cost,manual_minutes,automated_minutes,source_type) VALUES(?,?,?,?,?,?,?,?,?,'Illustrative')", (name,description,category,inputs,outputs,frequency,cost,manual,automated))
