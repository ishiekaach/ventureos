PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    industry TEXT NOT NULL DEFAULT 'Other',
    stage TEXT NOT NULL DEFAULT 'Pre-seed',
    location TEXT DEFAULT '',
    business_model TEXT DEFAULT '',
    website TEXT DEFAULT '',
    founded_year INTEGER,
    employee_count INTEGER,
    description TEXT DEFAULT '',
    source_type TEXT NOT NULL DEFAULT 'Illustrative',
    pipeline_status TEXT NOT NULL DEFAULT 'New',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS financial_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    revenue REAL,
    cogs REAL,
    operating_income REAL,
    depreciation_amortization REAL DEFAULT 0,
    ebitda REAL,
    cash_balance REAL,
    monthly_net_burn REAL,
    customer_count INTEGER,
    source_type TEXT NOT NULL DEFAULT 'Illustrative',
    UNIQUE(company_id, period)
);
CREATE TABLE IF NOT EXISTS screenings (
    screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    score REAL,
    thesis TEXT DEFAULT '',
    decision TEXT NOT NULL DEFAULT 'Needs review',
    notes TEXT DEFAULT '',
    screening_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS research_sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_url TEXT DEFAULT '',
    source_type TEXT DEFAULT 'User-provided',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS investment_memos (
    memo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Draft',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS agents (
    agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'Research',
    owner TEXT DEFAULT 'Unassigned',
    inputs TEXT DEFAULT '',
    outputs TEXT DEFAULT '',
    model_name TEXT DEFAULT 'Not specified',
    frequency_per_month REAL DEFAULT 0,
    monthly_cost REAL DEFAULT 0,
    manual_minutes REAL DEFAULT 0,
    automated_minutes REAL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'Active',
    source_type TEXT NOT NULL DEFAULT 'Illustrative',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS agent_overlaps (
    overlap_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_a INTEGER NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    agent_b INTEGER NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    similarity REAL NOT NULL,
    explanation TEXT DEFAULT '',
    recommendation TEXT DEFAULT 'Investigate further',
    reviewed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_a, agent_b),
    CHECK(agent_a < agent_b)
);
CREATE TABLE IF NOT EXISTS workflow_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL REFERENCES agents(agent_id) ON DELETE CASCADE,
    run_status TEXT NOT NULL DEFAULT 'Completed',
    duration_seconds REAL DEFAULT 0,
    cost REAL DEFAULT 0,
    executed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS investments (
    investment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    investment_amount REAL NOT NULL,
    pre_money_valuation REAL NOT NULL,
    post_money_valuation REAL NOT NULL,
    initial_ownership REAL NOT NULL,
    investment_date TEXT DEFAULT '',
    exit_valuation REAL,
    exit_date TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS funding_rounds (
    round_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investment_id INTEGER NOT NULL REFERENCES investments(investment_id) ON DELETE CASCADE,
    round_name TEXT NOT NULL,
    amount_raised REAL DEFAULT 0,
    dilution_pct REAL NOT NULL DEFAULT 0,
    round_date TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    action TEXT NOT NULL,
    details TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comps (
    comp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    enterprise_value REAL,
    revenue REAL,
    ebitda REAL,
    source_url TEXT DEFAULT '',
    as_of_date TEXT DEFAULT '',
    source_type TEXT NOT NULL DEFAULT 'User-entered'
);
