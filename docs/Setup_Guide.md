 Setup Guide
## Data Governance & Compliance Platform

**Author:** Osman Yildiz

---

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Git
- Windows 10/11

---

## Step-by-Step Installation

### 1. Install Python

1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Verify: `python --version`

### 2. Install PostgreSQL

1. Download from https://www.postgresql.org/download/windows/
2. Run installer
3. Set password (remember it!)
4. Default port: 5432
5. Install pgAdmin 4

### 3. Clone Repository
```bash
git clone https://github.com/oseyosman/DataGovernancePlatform.git
cd DataGovernancePlatform
```

### 4. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 5. Configure Environment

Edit `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/data_governance_db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-key
```

### 6. Create Database
```bash
# Open PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE data_governance_db;
\q
```

### 7. Initialize Database
```bash
# In backend folder with venv activated
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 8. Run Application
```bash
python run.py
```

Visit: http://localhost:5000/health

---

## Testing

### Create Admin User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@example.com","password":"Admin123!","role":"admin"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}'
```

---

## Troubleshooting

**Python not found:**
- Reinstall with "Add to PATH" checked

**PostgreSQL connection error:**
- Check PostgreSQL is running
- Verify password in `.env`

**Port 5000 in use:**
- Change port in `run.py`

---

## Next Steps

1. Test all API endpoints
2. Add more models (Data Quality, Compliance)
3. Start frontend development (React)
4. Write weekly status report