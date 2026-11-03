from database.db import init_db, execute, query_df

COMPANIES = [
    ("Northstar Workflow AI", "Enterprise Software", "Seed", "San Francisco, CA", "B2B SaaS", "https://example.com", 2023, 18, "AI workflow orchestration for mid-market operations teams."),
    ("Lumen Robotics", "Hardware", "Pre-seed", "Oakland, CA", "Robotics-as-a-Service", "https://example.com", 2024, 9, "Autonomous inspection robotics for industrial facilities."),
    ("LedgerLeaf", "Fintech", "Series A", "New York, NY", "B2B SaaS", "https://example.com", 2021, 42, "Financial operations software for growing businesses."),
    ("CarePath Systems", "Healthcare", "Seed", "San Jose, CA", "B2B SaaS", "https://example.com", 2022, 22, "Workflow tools for outpatient care coordination."),
    ("CarbonCurrent", "Climate Tech", "Pre-seed", "Denver, CO", "Usage-based", "https://example.com", 2024, 7, "Monitoring software for industrial energy efficiency."),
    ("VectorForge", "Enterprise Software", "Series A", "Seattle, WA", "B2B SaaS", "https://example.com", 2020, 55, "Developer infrastructure for enterprise AI deployments."),
    ("ParcelPilot", "Logistics", "Seed", "Austin, TX", "Transaction-based", "https://example.com", 2022, 16, "Route optimization for regional delivery operators."),
    ("BrightBench", "Education", "Pre-seed", "Boston, MA", "B2B SaaS", "https://example.com", 2024, 6, "Assessment and tutoring tools for technical education."),
    ("SignalHarbor", "Cybersecurity", "Seed", "San Francisco, CA", "B2B SaaS", "https://example.com", 2023, 14, "Security posture monitoring for cloud-native teams."),
    ("Morrow Materials", "Advanced Materials", "Seed", "Palo Alto, CA", "Licensing", "https://example.com", 2022, 12, "Materials discovery platform for industrial applications."),
    ("Fieldwise", "Agriculture", "Series A", "Sacramento, CA", "Hardware + SaaS", "https://example.com", 2021, 38, "Precision agriculture analytics and sensor systems."),
    ("OrbitOps", "Enterprise Software", "Seed", "Los Angeles, CA", "B2B SaaS", "https://example.com", 2023, 20, "Operations planning software for distributed teams."),
]
AGENTS = [
    ("Company Research Agent", "Summarizes company profiles, products, business models, and public research for investment screening.", "Company Research", "Investment Team", "Company URL and notes", "Company summary and key facts", "LLM", 80, 18, 35, 5),
    ("Competitor Mapping Agent", "Identifies competitors and compares products, target customers, positioning, and differentiation.", "Market Research", "Investment Team", "Company profile and market", "Competitor landscape", "LLM", 45, 12, 50, 8),
    ("Pitch Deck Summarizer", "Extracts key claims, traction metrics, business model, team details, and risks from pitch decks.", "Pitch Analysis", "Associate A", "Pitch deck PDF", "Structured pitch summary", "LLM + PDF parser", 60, 22, 40, 6),
    ("Investment Memo Drafter", "Turns company research and screening notes into a structured first-draft investment memo.", "Investment Writing", "Associate B", "Research notes and metrics", "Investment memo draft", "LLM", 30, 15, 90, 15),
    ("Financial Data Extractor", "Extracts historical revenue, margins, cash, and operating metrics from supplied financial files.", "Financial Analysis", "Finance Team", "Financial statements", "Normalized financial data", "Python + LLM", 35, 8, 55, 10),
    ("Founder Background Research", "Organizes founder biographies, prior roles, domain experience, and supplied public profile links.", "Founder Research", "Investment Team", "Founder names and links", "Founder research brief", "LLM", 25, 7, 30, 5),
    ("Market Sizing Assistant", "Structures bottom-up and top-down market sizing assumptions and highlights unsupported inputs.", "Market Research", "Associate A", "Market assumptions and sources", "TAM/SAM/SOM worksheet", "LLM + Python", 20, 10, 70, 12),
    ("Portfolio Update Generator", "Drafts periodic portfolio company updates from manually supplied operating metrics.", "Portfolio Monitoring", "Platform Team", "Portfolio KPI data", "Portfolio update draft", "LLM", 18, 9, 60, 10),
    ("Meeting Notes Organizer", "Converts supplied founder meeting notes into summaries, follow-ups, and open diligence questions.", "Administrative", "Investment Team", "Meeting notes", "Summary and action items", "LLM", 70, 20, 25, 4),
    ("Research Brief Generator", "Creates concise company and industry research briefs from supplied links and notes.", "Company Research", "Associate B", "Company links and notes", "Research brief", "LLM", 40, 11, 45, 7),
    ("Comparable Company Helper", "Organizes selected public comparable company metrics and calculates valuation multiples.", "Financial Analysis", "Finance Team", "Comps data", "Comparable company table", "Python", 15, 5, 50, 5),
    ("Diligence Question Builder", "Generates follow-up diligence questions based on a company's business model, risks, and missing information.", "Investment Writing", "Investment Team", "Company profile and memo", "Diligence question list", "LLM", 35, 8, 30, 5),
]

def seed():
    init_db()
    if not query_df("SELECT company_id FROM companies LIMIT 1").empty:
        return
    for i, row in enumerate(COMPANIES):
        cid = execute("INSERT INTO companies(name,industry,stage,location,business_model,website,founded_year,employee_count,description,source_type,pipeline_status) VALUES(?,?,?,?,?,?,?,?,?,'Illustrative',?)",
                      (*row, ["New", "Initial Screening", "Under Evaluation", "Due Diligence"][i % 4]))
        base = [1_200_000, 600_000, 4_500_000, 1_800_000, 350_000, 8_000_000, 950_000, 280_000, 1_500_000, 500_000, 5_500_000, 2_100_000][i]
        execute("INSERT INTO financial_metrics(company_id,period,revenue,cogs,operating_income,depreciation_amortization,ebitda,cash_balance,monthly_net_burn,customer_count,source_type) VALUES(?,?,?,?,?,?,?,?,?,?, 'Illustrative')",
                (cid, "FY2025", base, base*0.35, -base*0.18, base*0.03, -base*0.15, base*0.65, base*0.025, 20+i*13))
        execute("INSERT INTO financial_metrics(company_id,period,revenue,cogs,operating_income,depreciation_amortization,ebitda,cash_balance,monthly_net_burn,customer_count,source_type) VALUES(?,?,?,?,?,?,?,?,?,?, 'Illustrative')",
                (cid, "FY2026E", base*1.65, base*0.52, -base*0.08, base*0.04, -base*0.04, base*0.40, base*0.018, 35+i*18))
    for row in AGENTS:
        execute("INSERT INTO agents(name,description,category,owner,inputs,outputs,model_name,frequency_per_month,monthly_cost,manual_minutes,automated_minutes,source_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,'Illustrative')", row)

if __name__ == "__main__":
    seed()
