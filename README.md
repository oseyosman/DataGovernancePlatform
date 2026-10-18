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

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **API Backend** | Python 3.11+, Flask 3.0, Flask-JWT-Extended, Flask-CORS |
| **Database & ORM** | SQLAlchemy, Flask-Migrate (Alembic); SQLite by default, PostgreSQL supported |
| **Scraping & Parsing** | requests, BeautifulSoup4, PyPDF2 |
| **Data Exports** | pandas, openpyxl, fpdf2 |
| **Frontend Client** | Single-page HTML5, CSS3, Vanilla JavaScript in `client/`, served by Flask at `/` |
| **Testing** | pytest (34 unit and security tests) |

---

## Project Structure

```
DataGovernancePlatform/
├── backend1/
│   ├── app/
│   │   ├── models/        # User, Company, AnnualReport, Report, Alert, Activity
│   │   ├── routes/        # auth, admin, companies, reports, dashboard, alerts
│   │   └── services/      # scraper, parser, compliance_analyzer
│   ├── database/          # schema.sql, seed_db.sql
│   ├── migrations/        # Alembic database migrations
│   ├── config.py          # Application configuration
│   ├── requirements.txt   # Backend dependencies
│   └── seed_alerts_and_activities.py
├── client/                # Dashboard interface (index.html, style.css)
├── docs/                  # API_Documentation.md, Setup_Guide.md
├── scripts/               # Seeding, debugging, and manual verification scripts
├── tests/                 # pytest test suite (test_auth.py, test_security.py)
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

Run migrations from the `backend1` directory:

```bash
cd backend1 && flask db upgrade && cd ..
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

---

## Running Tests

Execute the automated test suite with pytest from the repository root:

```bash
pytest
```

The suite includes 34 tests covering:
- Authentication & JWT token handling
- Role-based authorization & admin access controls
- Password hashing & complexity validation
- CSRF safety (header-based JWT vs. cookies)
- Security headers and sensitive error response suppression

---

## Project Status

- [x] **Phase 1: Planning & Architecture** — Scope definition, database schema design, and compliance framework mapping.
- [x] **Phase 2: Backend Development** — Flask REST API, JWT authentication, 10-K scraping pipeline, and PDF text keyword parser.
- [x] **Phase 3: Web Dashboard Frontend** — Single-page dashboard in `client/` integrating metrics, report workflow, company directory, and alert feeds.
- [x] **Phase 4: Integration, RBAC & Security Testing** — Full end-to-end integration, role-based controls, export generation (CSV/Excel/PDF), and automated security test suite (34/34 passing).
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

---

## Contact

**Osman Yildiz**  
Email: [oseyosmanyildiz@gmail.com](mailto:oseyosmanyildiz@gmail.com)  
GitHub: [https://github.com/oseyosman](https://github.com/oseyosman)

