# VentureOS

**Investment Intelligence & AI Operations Platform** — a Python and Streamlit portfolio project combining startup screening, financial analysis, AI-assisted research, and AI workflow inventory/optimization.

> VentureOS is an educational prototype. All seeded companies, financial metrics, agents, costs, and workflow assumptions are synthetic. It is not affiliated with any investment firm and does not provide investment advice.

## What it is designed to demonstrate

- Startup deal-flow tracking and screening workflows.
- Company-level financial snapshots and diligence notes.
- Gross profit, gross margin, EBITDA, EBITDA margin, and cash runway calculations.
- Venture return modeling with ownership dilution, exit proceeds, MOIC, and simplified annualized IRR.
- Exit valuation and dilution sensitivity analysis.
- An AI-agent inventory with owners, inputs, outputs, usage, cost, and status.
- Text-similarity triage for potentially overlapping AI workflows, with human review.
- Estimated workflow time savings and labor value based on explicit user-entered assumptions.
- Optional LLM-assisted research drafts based on user-provided context.
- Excel model generation/import and CSV exports.

## Data and responsible-use notes

The seeded companies, financial metrics, AI agents, costs, and workflow assumptions are synthetic examples. Replace them with sourced data before using the analysis for any real decision. Similarity scores are triage signals, not proof that two agents duplicate one another. AI-generated research is not independently verified and should be checked against primary sources. The financial model is simplified and is not investment advice.

Do not enter confidential company, customer, employee, or investment information into a public demo. The optional OpenAI API integration requires a user-supplied key and may incur usage charges; the core app is designed to work without one.

## Project structure

- `app.py` — Streamlit interface and page routing.
- `database/` — SQLite schema, connection management, and synthetic seed data.
- `modules/` — financial calculations, AI research, overlap detection, and efficiency estimates.
- `utils/` — formatting and Excel workbook generation.
- `tests/` — unit tests for financial calculations and overlap detection.

## Run locally

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Optional AI configuration

Create a local `.env` file (never commit it) with:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

The AI research feature analyzes context supplied by the user; it does not browse the web or independently verify claims. Without a key, the app uses an offline template.

## Excel workflow

1. Open **Excel & Data** in the app and download the financial model template.
2. Replace sample rows with sourced assumptions.
3. Clearly label actual, estimated, and illustrative values.
4. Keep the required column names in the Financials worksheet before importing.

## Free deployment

The intended hosting target is Streamlit Community Cloud, connected to this public GitHub repository. Set the app entry point to `app.py`. No API key is needed for the core demo.

Streamlit Community Cloud has resource and sleep limits. Local SQLite data is not durable on hosted ephemeral storage, so records entered by visitors may be lost after restarts or redeployments. The demo reseeds its synthetic dataset when the database is empty. A production version should use managed persistent storage such as PostgreSQL.

## Tests

```bash
pytest -q
```

## Known limitations and next steps

- Company research currently relies on user-provided context rather than automated web research or source verification.
- Financial calculations do not model full cap tables, liquidation preferences, carry, fund-level cash flows, or detailed accounting adjustments.
- A production deployment should add authentication, durable database storage, source-level citations, and stronger audit logging.
