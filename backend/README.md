# MediAccess Backend (Flask + MongoDB)

Production-style REST backend for the Patient Access Management platform.

## Features
- Flask application factory pattern
- MongoDB persistence with `pymongo`
- Role-aware login endpoint (patient / validator / admin / analyst)
- Patient application submission and status tracking
- Validator review workflow (approve/reject)
- Admin approved-claims report
- Analyst KPI + status distribution APIs
- Health check and seed endpoint

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app:create_app run
```

Server starts at `http://127.0.0.1:5000`.

## Key Endpoints

- `GET /api/v1/health`
- `POST /api/v1/auth/login`
- `POST /api/v1/seed`
- `GET /api/v1/patients/<email>/application`
- `POST /api/v1/patients/<email>/application`
- `GET /api/v1/reports`
- `PATCH /api/v1/reports/<report_id>/decision`
- `GET /api/v1/admin/approved-claims`
- `GET /api/v1/analytics/summary`

## Environment

| Variable | Description |
|---|---|
| `MONGO_URI` | Mongo server URI |
| `MONGO_DB_NAME` | Database name |
| `API_PREFIX` | API prefix (default `/api/v1`) |

## Notes
- For local frontend integration, point fetch calls to this API.
- Mongo collections used: `users`, `applications`, `validator_reports`.
