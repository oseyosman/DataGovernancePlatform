# Data Governance & Compliance Platform

**Author:** Osman Yildiz  

## Project Overview

A web-based platform for managing data quality, access controls, and regulatory compliance with ISO 27001/27017 standards.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/oseyosman/DataGovernancePlatform.git
cd DataGovernancePlatform
```

2. Set up backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. Configure environment:
- Copy `.env.example` to `.env`
- Update database credentials

4. Create database:
```bash
psql -U postgres
CREATE DATABASE data_governance_db;
\q
```

5. Initialize database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Run application:
```bash
python run.py
```

Visit: http://localhost:5000/health

## Technology Stack

- **Backend:** Python Flask 3.0
- **Database:** PostgreSQL 15+
- **Authentication:** JWT (Flask-JWT-Extended)
- **Frontend:** React 18+ (Coming in Phase 3)

## Project Status

- ✅ Phase 1: Planning (Weeks 1-2)
- 🔄 Phase 2: Backend Development (Weeks 3-5)
- ⏳ Phase 3: Frontend Development (Weeks 6-8)
- ⏳ Phase 4: Integration & Testing (Weeks 7-9)
- ⏳ Phase 5: Documentation & Demo (Weeks 10-11)

## Contact

Osman Yildiz  
Email: oseyosmanyildiz@gmail.com  
GitHub: https://github.com/oseyosman
