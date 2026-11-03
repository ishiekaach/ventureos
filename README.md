# VentureOS

**Investment Intelligence & AI Operations Platform** — an independent Python and Streamlit portfolio project combining startup screening, financial analysis, AI-assisted research, and AI workflow inventory/optimization.

> VentureOS is an educational prototype. All seeded companies, financial metrics, agents, costs, and workflow assumptions are synthetic. It is not affiliated with any investment firm and does not provide investment advice.

## Features

- Startup deal-flow database with industry, stage, and pipeline filters.
- Company analysis with screening notes and diligence questions.
- Operating metric calculator: gross profit, gross margin, EBITDA, EBITDA margin, and cash runway.
- Venture return calculator with ownership dilution, proceeds, MOIC, and simplified annualized IRR.
- Exit valuation / dilution sensitivity analysis.
- AI agent registry with owners, inputs, outputs, usage, cost, and status.
- Offline TF-IDF/cosine-similarity workflow overlap triage.
- Efficiency estimates based on user-entered workflow assumptions.
- Optional LLM-assisted research drafts (requires user-supplied API key; app works without it).
- Excel template download and financial metrics import.
- CSV exports and SQLite persistence.

## Free local setup

Requires Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

The app seeds a local SQLite database with clearly labeled illustrative data on first run.

## Optional AI configuration

Copy `.env.example` to `.env` and add an API key for a compatible OpenAI account:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
```

The AI research feature only analyzes context supplied by the user; it does not browse the web or independently verify claims. API usage may incur charges. Without a key, the app uses a no-cost offline template. Financial calculations and overlap detection run locally.

## Excel workflow

1. Open **Excel & Data** in the app.
2. Download `VentureOS_Financial_Model_Template.xlsx`.
3. Replace example rows with your own sourced assumptions and label actual, estimated, and illustrative data.
4. Keep the required column names in the `Financials` worksheet.
5. Upload the workbook to import metrics for companies already in the database.

## Deployment: Streamlit Community Cloud

1. Push this repository to a public GitHub repository.
2. Sign in to Streamlit Community Cloud with GitHub.
3. Create an app using this repository, branch `main`, and `app.py` as the entry point.
4. Deploy. No API key is required for the core demo.
5. If enabling LLM research, add `OPENAI_API_KEY` and `OPENAI_MODEL` under the app's Secrets settings. Do not commit `.env` or secrets.

Free hosting has resource, sleep, and availability limits. Streamlit Community Cloud does not guarantee persistence of local file storage, so demo records entered by visitors may be lost at any time. The app automatically reseeds its synthetic demonstration dataset when the local database is empty. Do not enter confidential information or rely on the hosted SQLite database for durable records. A later production version should use a managed PostgreSQL database or another persistent data store.

## Tests

```bash
pytest -q
```

## Architecture

- `app.py`: Streamlit interface and page routing.
- `database/`: SQLite schema, connection management, and synthetic seed data.
- `modules/`: Financial calculations, AI research, overlap detection, and efficiency estimates.
- `utils/`: formatting and Excel workbook generation.
- `tests/`: unit tests for financial calculations and overlap detection.

## Known limitations / next improvements

- Similarity scores are text-based triage signals, not proof of functional duplication.
- Company research is based on user-provided context; no web crawler or source verification is included.
- Financial models are simplified and do not cover full cap tables, liquidation preferences, carry, fund-level cash flows, or accounting adjustments.
- A future version should add source-level citations, more complete cap-table modeling, public-company comps ingestion, authentication, and durable hosted database storage.
