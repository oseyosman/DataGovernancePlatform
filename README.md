# Data Governance & Compliance Platform

A Flask REST API with a lightweight, responsive web dashboard for tracking data-governance reports, role-based access control (RBAC), and regulatory compliance indicators for public companies. The platform scrapes annual reports (10-K) from AnnualReports.com, parses PDF report text for framework-specific compliance keywords (ISO 27001, NIST CSF, SOC 2, COSO, GDPR/CCPA), and presents the findings alongside a report review workflow and audit logging.

Built as the capstone project for the MSIT program at Walsh College.  
**Author:** Osman Yildiz (<oseyosmanyildiz@gmail.com>)

> **Topics:** `data-governance`, `compliance-monitoring`, `iso-27001`, `nist-csf`, `soc-2`, `coso`, `flask-api`, `web-scraping`, `pdf-parser`, `role-based-access-control`, `python`, `sqlite`, `postgresql`, `vanilla-javascript`

---

## Features

- **Authentication & Role-Based Access Control (RBAC):** JWT access and refresh tokens, password-strength validation, hashed credentials, user vs. admin roles, and admin-only user management endpoints.
- **Company & Annual Report Pipeline:** Search and scrape company profiles and 10-K annual reports from AnnualReports.com, retrieve PDF links, and extract compliance keywords using a PDF text parser.
- **Heuristic Compliance Scoring:** Multi-framework scoring model (ISO 27001, NIST CSF, SOC 2, COSO) combining industry baselines, company size, report coverage, and keyword occurrences. *(Scores are illustrative indicators for governance analysis, not formal audit certifications).*
- **Report Lifecycle Workflow:** Create, upload, submit, review, approve/reject, and export governance reports in CSV, Excel, and PDF formats.
- **Dashboard & Alert Monitoring:** Overview metrics, severity-categorized alert notifications with read/unread tracking, and user activity audit logging.
- **Security & Quality Testing:** Comprehensive automated test suite verifying authentication bypass prevention, RBAC enforcement, password hashing, JWT header validation, CSRF immunity, and error-handling leakage.
- **Grounded Q&A (RAG):** Ask questions about ingested reports and get answers with page-level citations, or an explicit refusal when the evidence is weak. See [Question answering (RAG)](#question-answering-rag).

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **API Backend** | Python 3.11+, Flask 3.0, Flask-JWT-Extended, Flask-CORS |
| **Database & ORM** | SQLAlchemy, Flask-Migrate (Alembic); SQLite by default, PostgreSQL supported |
| **Scraping & Parsing** | requests, BeautifulSoup4, PyPDF2 |
| **Data Exports** | pandas, openpyxl, fpdf2 |
| **Retrieval & QA** | BM25 (pure Python); offline extractive answerer or Anthropic API |
| **Frontend Client** | Single-page HTML5, CSS3, Vanilla JavaScript in `client/`, served by Flask at `/` |
| **Testing & CI** | pytest (87 unit, security, and RAG tests), GitHub Actions, Docker |

---

## Project Structure

```
DataGovernancePlatform/
├── backend1/
│   ├── app/
│   │   ├── models/        # User, Company, AnnualReport, Report, Alert, Activity, RagChunk, RagQueryLog
│   │   ├── routes/        # auth, admin, companies, reports, dashboard, alerts, rag
│   │   └── services/      # scraper, parser, compliance_analyzer, rag/
│   ├── database/          # schema.sql, seed_db.sql
│   ├── migrations/        # Alembic database migrations
│   ├── config.py          # Application configuration
│   ├── init_db.py         # Database initialization helper
│   ├── requirements.txt   # Backend dependencies
│   └── seed_alerts_and_activities.py
├── client/                # Dashboard interface (index.html, style.css)
├── docs/                  # API_Documentation.md, Setup_Guide.md
├── evals/                 # RAG evaluation harness, fixtures and saved reports
├── scripts/               # Seeding, debugging, and RAG command-line helpers
├── tests/                 # pytest test suite (test_auth.py, test_security.py, test_rag.py)
├── Dockerfile             # Container configuration
├── .dockerignore          # Docker build ignore rules
├── pytest.ini             # Pytest test discovery configuration
├── run.py                 # Application root entry point
├── QUICKSTART.md          # Guide for scraping and quickstart
└── SEEDING.md             # Instructions for database seeding
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Git
- SQLite (built-in default) or PostgreSQL 15+

### 2. Installation

Clone the repository and prepare your virtual environment:

```bash
git clone https://github.com/oseyosman/DataGovernancePlatform.git
cd DataGovernancePlatform

python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r backend1/requirements.txt
```

### 3. Initialize the Database

Initialize tables and schema using the initialization helper:

```bash
python backend1/init_db.py       # creates all tables
```

### 4. Seed Initial Data (Optional)

Run seeding helpers from the project root:

```bash
# Scrape and seed real company data with annual reports
python scripts/seed_companies.py

# Seed initial dashboard alerts and activity audit logs
python backend1/seed_alerts_and_activities.py
```

*Note: Seed scripts create local development accounts with default passwords. Use only for development and testing.*

### 5. Run the Application

Launch the platform using the root entry point:

```bash
python run.py
```

Access the application in your browser:
- **Web Dashboard:** [http://localhost:5000/](http://localhost:5000/)
- **Health Check:** [http://localhost:5000/health](http://localhost:5000/health)
- **API Base:** [http://localhost:5000/api](http://localhost:5000/api)

---

## Configuration

Settings are managed via environment variables with defaults in `backend1/config.py`:

| Variable | Description | Default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session secret key | Auto-generated development key |
| `JWT_SECRET_KEY` | JWT token signature key | Auto-generated development key |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///data_governance.db` |
| `PORT` | Web server port | `5000` |
| `RAG_LLM_PROVIDER` | Answer generation provider (`extractive` or `anthropic`) | `extractive` |
| `RAG_LLM_MODEL` | Model identifier for Anthropic provider | Model default |
| `ANTHROPIC_API_KEY` | API key for Anthropic provider | None |
| `RAG_ALLOWED_HOSTS` | Comma-separated hosts allowed for report ingest | `annualreports.com` |
| `RAG_MIN_COVERAGE` | Share of question terms required in evidence | `0.5` |

Docker (single worker, since signing keys are generated per process unless you set them):

```bash
docker build -t data-governance-platform .
docker run -p 5000:5000 -e SECRET_KEY=... -e JWT_SECRET_KEY=... data-governance-platform
```

---

## Running Tests

Execute the automated test suite with pytest from the repository root:

```bash
pytest
```

The suite has 87 tests: authentication, authorization, password hashing, JWT configuration, security headers and error handling, plus the RAG chunker, retriever, guardrails, API and evaluation gate.

---

## Question answering (RAG)

Ask a question about a company's annual report and get a short answer with citations back to the source passage and page, or a refusal when the reports do not support an answer.

```
POST /api/rag/ask   {"question": "...", "company_id": 1, "top_k": 4}      (any signed-in user)
POST /api/rag/ingest/<report_id>                                           (admin)
GET  /api/rag/stats                                                        (admin)
```

**Pipeline:** PDF text, split into sentence-aligned chunks that keep their page number, indexed with BM25. A question is validated, retrieved against (optionally scoped to one company), and passed through these checks before any answer is returned:

1. **Evidence gate:** abstain if too few of the question's terms appear in the retrieved text. The gate is measured *after* sanitizing, on exactly what the model would see.
2. **Prompt-injection filtering:** sentences in retrieved text that look like instructions to the model are removed, and passages are wrapped in escaped `<source>` tags and presented as untrusted data.
3. **Grounded generation:** the model is told to answer only from the numbered sources and to say `INSUFFICIENT_EVIDENCE` otherwise.
4. **Citation check:** an answer with no valid `[n]` citation is rejected.

**Operations:** every query logs latency, passages used, abstention reason, provider, model and token counts to `rag_query_logs` (summarized at `/api/rag/stats`). Ingest only downloads from allowlisted hosts over HTTPS (`RAG_ALLOWED_HOSTS`, default `annualreports.com`) and refuses redirects, to block server-side request forgery. Provider errors return generic messages and are logged server-side.

**Providers** (`RAG_LLM_PROVIDER`):

| Value | Behavior |
| --- | --- |
| `extractive` (default) | Offline, no key. Returns the best-matching sentence(s) verbatim with citations. A baseline, not a language model. |
| `anthropic` | Calls the Anthropic API (`pip install anthropic`; set `ANTHROPIC_API_KEY`, optionally `RAG_LLM_MODEL`). Request construction is unit-tested against a stand-in SDK; it has **not** been run against the live API. |

Try it without a server:

```bash
python scripts/rag_cli.py ingest-file path/to/10k.pdf --company "Acme Corp" --year 2024
python scripts/rag_cli.py ask "How does the board oversee cybersecurity?" --company-id 1
```

### Evaluation

`python -m evals.run_eval` scores the pipeline on 35 hand-written questions and writes `evals/results/latest.md`. It reports retrieval recall@k and MRR, answer accuracy, citation precision, false abstentions, correct abstention on unanswerable questions, prompt-injection leakage, latency and tokens, with a per-category breakdown and a list of failures. CI fails if any metric drops below its threshold.

Results with the offline extractive baseline (`evals/results/latest.md`):

| Metric | First run | After fixes |
| --- | --- | --- |
| Retrieval recall@4 | 96% | 96% |
| Answer accuracy (string check) | 70% | 78% |
| False abstentions | 26% | 19% |
| Citation precision | 20% | 96% |
| Correct abstention on unanswerable | 88% | 100% |
| Injection leakage | 0% | 0% |

The first run exposed three defects, since fixed: the evidence gate was measured before sanitizing (a question made of the words in a planted instruction passed it), company names in a question counted against evidence even when the search was already scoped to that company, and the extractive baseline appended unrelated, wrongly cited sentences. The first-run report is kept in `evals/results/baseline_v0.md`.

**Read these numbers carefully.**

- The corpus is **synthetic**: 26 invented passages about three fictional companies (`evals/fixtures/`). It exists so tests and CI run offline and deterministically. It is not real filing data, and the figures above say nothing about performance on real 10-Ks.
- The questions were written alongside the corpus, and the fixes above were made while looking at these same questions. Treat the "after" column as a regression baseline, not evidence of generalization.
- Paraphrased questions fail by design of keyword retrieval ("data leak" does not match "breach"; "two-step login" does not match "multi-factor"): 0 of 4 are answered. The evidence gate is lexical too, so a stronger model would not rescue them. Embedding-based retrieval is the next step.
- Answer accuracy is a string check against required phrases. It is strict for fluent model output and should be supplemented with human or model-graded review.

To evaluate on real data, ingest reports, write questions with `relevant_phrases` instead of `gold_chunk_ids`, and run `python -m evals.run_eval --corpus db --questions my_questions.json`. Add `--provider anthropic` to compare a real model against the baseline.

---

## Project Status

- [x] **Phase 1: Planning & Architecture** — Scope definition, database schema design, and compliance framework mapping.
- [x] **Phase 2: Backend Development** — Flask REST API, JWT authentication, 10-K scraping pipeline, and PDF text keyword parser.
- [x] **Phase 3: Web Dashboard Frontend** — Single-page dashboard in `client/` integrating metrics, report workflow, company directory, and alert feeds.
- [x] **Phase 4: Integration, RBAC & Security Testing** — Full end-to-end integration, role-based controls, export generation (CSV/Excel/PDF), and automated security test suite (87 tests passing).
- [x] **Phase 5: Documentation & Repo Maintenance** — API reference, clean repository layout, environment instructions, and seed tooling.

---

## API Documentation

Interactive endpoint details and curl examples are documented in [docs/API_Documentation.md](docs/API_Documentation.md). Core route prefixes include:
- `/api/auth` — Registration, authentication, token refresh, and user profile
- `/api/admin` — User management and system administration (admin only)
- `/api/companies` — Company profiles and annual report listings
- `/api/reports` — Report CRUD, review workflow, and CSV/Excel/PDF export
- `/api/dashboard` — Overview metrics, trends, and compliance summaries
- `/api/alerts` — System alert notifications and status updates
- `/api/rag` — Grounded question answering, document ingestion, and telemetry

---

## Known Limitations

- The dashboard trend chart and some change indicators use placeholder values; only the headline metrics are computed from the database.
- Compliance scores are heuristic (see above) and should not be read as audit findings.
- `flask db upgrade` cannot build a database from scratch (the first migration assumes existing tables); use `python backend1/init_db.py` for new databases. Migrations are only for upgrading databases that already follow the chain.
- The Dockerfile has not been built in the environment where it was written (no Docker daemon); CI builds and smoke-tests it.

---

## Contact

**Osman Yildiz**  
Email: [oseyosmanyildiz@gmail.com](mailto:oseyosmanyildiz@gmail.com)  
GitHub: [https://github.com/oseyosman](https://github.com/oseyosman)


