# Sentinel SOS — Intelligent Emergency-Response Backend

Sentinel SOS is an intelligent emergency-response management backend engineered with **FastAPI**, **PostgreSQL** (via SQLAlchemy & Alembic), and **MongoDB** (via PyMongo). The system allows citizens to trigger emergency SOS alerts, notify emergency contacts, match eligible nearby responders via spatial and road routing, and provide live incident tracking.

---

## 1. Project Directory Structure & Component Responsibilities

```
sentinel-sos/ (backend/)
├── .env                          # Local secrets (never committed to git)
├── .env.example                  # Environment configuration template
├── .gitignore                    # Excludes venvs, secrets, databases, logs
├── requirements.txt              # Production and test dependencies
├── README.md                     # Comprehensive backend documentation
├── Dockerfile                    # Containerization build specification
├── docker-compose.yml            # Multi-service stack (FastAPI, Postgres, Mongo)
├── alembic.ini                   # Relational database migration settings
│
├── app/                          # Core application package
│   ├── main.py                   # FastAPI initialization, lifespan & CORS
│   │
│   ├── core/                     # Foundational architecture modules
│   │   ├── config.py             # Pydantic Settings v2 configuration namespaces
│   │   ├── security.py           # Bcrypt password hashing & JWT token handling
│   │   ├── exceptions.py         # Custom domain exceptions & global handlers
│   │   ├── logging.py            # Structured system logging
│   │   └── dependencies.py       # FastAPI dependency injection (Auth, Roles)
│   │
│   ├── api/                      # REST API routing
│   │   └── v1/
│   │       ├── router.py         # Master router for API version 1
│   │       └── endpoints/
│   │           ├── health.py     # Liveness & readiness probes (DB checks)
│   │           ├── auth.py       # Registration, login & profile endpoints
│   │           ├── users.py      # User account profile updates
│   │           ├── sos.py        # SOS alert creation, status, cancel & events
│   │           ├── responders.py # Responder enrollment & GPS telemetry
│   │           ├── dispatch.py   # Nearby search, assignment dispatch & response
│   │           ├── contacts.py   # Citizen emergency contacts CRUD
│   │           ├── notifications.py # Notification dispatch testing & logs
│   │           ├── incidents.py  # Incident history retrieval
│   │           └── admin.py      # Admin dashboard & audit logging
│   │
│   ├── schemas/                  # Pydantic V2 data validation models
│   │   ├── auth.py               # Token & login request/response schemas
│   │   ├── user.py               # User serialization models
│   │   ├── incident.py           # SOS payload, status machine & event schemas
│   │   ├── responder.py          # Responder registration & telemetry models
│   │   ├── contact.py            # Emergency contact schemas
│   │   └── notification.py       # Notification dispatch payload schemas
│   │
│   ├── models/                   # Persistent domain entities
│   │   └── sql/                  # SQLAlchemy PostgreSQL models
│   │       ├── base.py           # UUID & timestamp mixins
│   │       ├── user.py           # Users table
│   │       ├── role.py           # Roles & permissions table
│   │       ├── responder.py      # Responders table (qualifications & status)
│   │       ├── contact.py        # Emergency contacts table
│   │       └── assignment.py     # Incident assignments & audit logs
│   │
│   ├── db/                       # Database engine and session management
│   │   ├── sql.py                # SQLAlchemy engine, SessionLocal & health check
│   │   └── mongodb.py            # PyMongo connection manager & health check
│   │
│   ├── repositories/             # Data access abstraction layer
│   │   ├── user_repository.py    # User SQL queries
│   │   ├── incident_repository.py# MongoDB SOS incidents & events
│   │   ├── responder_repository.py# Responder queries & telemetry persistence
│   │   └── contact_repository.py # Emergency contact queries
│   │
│   ├── services/                 # Business logic and domain orchestrators
│   │   ├── auth_service.py       # Authentication, hashing, JWT issuance
│   │   ├── sos_service.py        # Emergency state machine & idempotency
│   │   ├── dispatch_service.py   # Responder spatial matching & assignments
│   │   ├── location_service.py   # Haversine distance & coordinate validation
│   │   ├── incident_service.py   # Incident queries & history
│   │   ├── contact_service.py    # Contact ownership management
│   │   └── notification_service.py# Multi-channel notification delivery
│   │
│   ├── integrations/             # External third-party API adapters
│   │   ├── maps/
│   │   │   └── google_maps.py    # Google Geocoding & Routes ETA adapter
│   │   ├── messaging/
│   │   │   ├── sms.py            # Mock / Twilio / MSG91 SMS adapter
│   │   │   ├── push.py           # Firebase Cloud Messaging adapter
│   │   │   └── email.py          # Email notification client
│   │   └── ai/
│   │       └── emergency_classifier.py # LLM emergency classification
│   │
│   └── workers/                  # Background worker tasks
│       └── notification_worker.py# Asynchronous notification queue processor
│
├── migrations/                   # Alembic database migrations
│   ├── env.py                    # Alembic runtime environment
│   ├── script.py.mako            # Migration template
│   └── README                    # Migration instructions
│
├── tests/                        # Automated Pytest test suite
│   ├── conftest.py               # Fixtures, test database, auth headers
│   ├── test_config.py            # Settings validation & namespaces
│   ├── test_health.py            # Liveness & readiness probes
│   ├── test_auth.py              # User registration, login & JWT
│   ├── test_sos.py               # SOS creation, duplicate check, events
│   ├── test_dispatch.py          # Responder location & nearby search
│   ├── test_contacts.py          # Emergency contacts CRUD
│   └── test_notifications.py     # Notification dispatching
│
└── docs/                         # Architecture, security & setup specs
    ├── architecture.md           # System design & incident state machine
    ├── api-reference.md          # Complete REST API specifications
    ├── database-schema.md        # PostgreSQL & MongoDB schema definitions
    ├── setup-guide.md            # Windows setup & execution commands
    └── security.md               # Security checklist & key management
```

---

## 2. Environment Configuration Namespaces

All configuration is centralized in `app/core/config.py` using Pydantic Settings v2:

| Namespace | Variable | Default | Purpose |
| :--- | :--- | :--- | :--- |
| **Application** | `SENTINEL_APP_NAME` | `Sentinel SOS Emergency Response API` | Application title |
| | `SENTINEL_ENV` | `development` | Profile (`development`, `testing`, `production`) |
| | `SENTINEL_API_PREFIX` | `/api/v1` | Master routing prefix |
| | `SENTINEL_DEBUG` | `False` | Debug mode |
| | `SENTINEL_ALLOWED_ORIGINS`| `["*"]` | CORS origin restrictions |
| **Relational DB** | `SQL_DATABASE_URL` | `sqlite:///./sentinel_dev.db` | PostgreSQL connection string |
| | `SQL_ECHO` | `False` | SQL statement logging |
| **MongoDB** | `MONGO_URI` | `mongodb://localhost:27017` | MongoDB connection URI |
| | `MONGO_DATABASE` | `sentinel_sos` | Incident document store database |
| **Auth** | `AUTH_SECRET_KEY` | *(dev placeholder)* | Min 32-character JWT secret |
| | `AUTH_ALGORITHM` | `HS256` | JWT signature algorithm |
| | `AUTH_TOKEN_EXPIRE_MINUTES`| `60` | Token expiration time |
| **Maps** | `MAPS_GOOGLE_API_KEY` | `""` | Google Maps Platform API Key |
| **SMS** | `SMS_PROVIDER` | `mock` | Active provider (`mock`, `twilio`, `msg91`) |
| | `SMS_TWILIO_ACCOUNT_SID` | `""` | Twilio Account SID |
| | `SMS_TWILIO_AUTH_TOKEN` | `""` | Twilio Auth Token |
| | `SMS_MSG91_API_KEY` | `""` | MSG91 Auth Key |
| **Push** | `PUSH_FCM_PROJECT_ID` | `""` | Firebase project ID |
| **AI / LLM** | `LLM_PROVIDER` | `mock` | Active provider (`mock`, `gemini`, `openai`) |

---

## 3. Quickstart Commands (Windows)

### 1. Install & Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configure Environment
```powershell
Copy-Item .env.example .env
```

### 3. Run Automated Tests
```powershell
python -m pytest -v
```

### 4. Start the Application
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Open Swagger Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Open Health Endpoint: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)
- Open Readiness Check: [http://127.0.0.1:8000/api/v1/health/readiness](http://127.0.0.1:8000/api/v1/health/readiness)

---

## 4. Docker Deployment
```powershell
docker compose up -d --build
```
This launches:
- `sentinel_sos_backend` on port `8000`
- `sentinel_sos_postgres` on port `5432`
- `sentinel_sos_mongo` on port `27017`
