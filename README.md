# Data Governance & Compliance Platform

**Author:** Osman Yildiz  

## Project Overview

A web-based platform for managing data quality, access controls, and regulatory compliance with ISO 27001/27017 standards. It includes automated data scraping from 10-K reports and a dashboard for compliance monitoring.

## Quick Start

### Prerequisites
- Python 3.11+
- SQLite (Default) or PostgreSQL 15+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/oseyosman/DataGovernancePlatform.git
cd DataGovernancePlatform
```

2. Set up backend:
```bash
cd backend1
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env.example` to `.env` (if available) or rely on defaults in `config.py`.
- The application defaults to SQLite for easy setup.

4. Initialize database:
```bash
flask db upgrade
```

5. Seed initial data (Optional):
```bash
python seed_companies.py
python seed_alerts_and_activities.py
```

6. Run application:
```bash
python run.py
```

Visit: http://localhost:5000/api/health

## Technology Stack

- **Backend:** Python Flask 3.0
- **Database:** SQLite (Dev), PostgreSQL (Prod)
- **Authentication:** JWT (Flask-JWT-Extended)
- **Frontend:** React 18+ (In Progress - see `client` directory)

## Project Status

- ✅ Phase 1: Planning (Completed)
- ✅ Phase 2: Backend Development (Core API, Scraper, Parser)
- ✅ Phase 3: Frontend Development (React Dashboard in progress)
- ✅ Phase 4: Integration & Full Testing (Completed)
- ✅ Phase 5: Documentation & Demo Prep

## Documentation

- [QUICKSTART.md](QUICKSTART.md) - Detailed guide for scraping real data.
- [SEEDING.md](SEEDING.md) - Instructions for populating the database.

## Contact

Osman Yildiz  
Email: oseyosmanyildiz@gmail.com  
GitHub: https://github.com/oseyosman
