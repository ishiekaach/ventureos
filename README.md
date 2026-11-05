# VentureOS

**Investment Intelligence + AI Operations** is an independent Python and Streamlit portfolio project for startup deal flow, company analysis, venture return modeling, AI research drafting, and AI workflow inventory.

> Educational prototype only. Seeded companies, financial metrics, AI agents, and workflow assumptions are synthetic. VentureOS is not affiliated with an investment firm and does not provide investment advice.

## Features

- Startup deal-flow database with industry, stage, and pipeline tracking.
- Company profiles and financial snapshots.
- Operating metrics: gross margin, EBITDA, and cash runway.
- Venture return model: post-money valuation, ownership dilution, exit proceeds, MOIC, and simplified annualized IRR.
- AI research drafts based only on user-provided context, with an offline mode.
- AI agent registry with workflow inputs/outputs, usage, cost, and estimated time savings.
- TF-IDF/cosine-similarity overlap triage for AI workflows.
- Excel financial model template and CSV exports.

## Local setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app creates a local SQLite database and seeds illustrative demo data on first run.

## Optional AI configuration

Copy `.env.example` to `.env` and add an OpenAI API key. Without a key, the research assistant uses an offline template. AI drafts only use context supplied by the user; they do not browse or independently verify facts. API usage may incur charges. Never commit API keys or secrets.

## Deployment

Deploy the public GitHub repository to Streamlit Community Cloud using branch `main` and `app.py` as the entry point. The core app does not require an API key.

Free hosting has resource and sleep limits. Local SQLite data on hosted apps is not durable and may be lost after restarts. Do not enter confidential information. A production version should use managed persistent storage such as PostgreSQL.

## Tests

Run `pytest -q`.

## Project structure

- `app.py`: Streamlit interface.
- `config.py`: application configuration.
- `database/`: SQLite schema, connection helpers, and demo seed data.
- `modules/`: financial calculations, AI research, workflow overlap, and efficiency estimates.
- `utils/`: formatting and Excel workbook generation.
- `tests/`: unit tests.

## Limitations

Similarity scores are text-based triage signals, not proof of duplicated functionality. Financial models are simplified and exclude full cap tables, liquidation preferences, fund-level cash flows, fees, and carry. Company research requires independent source verification.
