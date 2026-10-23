# Sentinel SOS — Setup & Deployment Guide

## 1. Local Development Setup (Windows)

### Prerequisites
- Python 3.11 or higher
- Git
- Optional: Docker Desktop (for PostgreSQL & MongoDB containers)

### Step 1: Clone and Navigate
```powershell
cd "backend"
```

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default local settings use SQLite (`sqlite:///./sentinel_dev.db`) and mock notification adapters so the backend runs immediately without external cloud credentials.

### Step 5: Run Database Migrations (Optional)
In development, database tables are automatically initialized during startup. To run Alembic explicitly:
```powershell
alembic upgrade head
```

### Step 6: Start FastAPI Server
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health probe: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

## 2. Running Automated Tests

Run the full pytest suite with verbose output:
```powershell
python -m pytest -v
```

---

## 3. Docker Compose Deployment

To run PostgreSQL, MongoDB, and Sentinel SOS Backend in isolated containers:
```powershell
docker compose up -d --build
```
Check container status:
```powershell
docker compose ps
docker compose logs -f backend
```
Stop services:
```powershell
docker compose down
```
