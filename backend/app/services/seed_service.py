from datetime import datetime, timezone

from app.utils.db import get_db

DEFAULT_USERS = [
    {"email": "patient1@example.com", "password": "pass", "role": "patient", "name": "New User"},
    {"email": "patient2@example.com", "password": "pass", "role": "patient", "name": "Rajan Menon"},
    {"email": "patient4@example.com", "password": "pass", "role": "patient", "name": "Karthik Raja"},
    {"email": "validator@med.com", "password": "pass", "role": "validator", "name": "Validator User"},
    {"email": "admin@med.com", "password": "admin123", "role": "admin", "name": "Admin User"},
    {"email": "analyst@med.com", "password": "analyst123", "role": "analyst", "name": "Analyst User"},
]


def ensure_indexes() -> None:
    db = get_db()
    db.users.create_index("email", unique=True)
    db.applications.create_index("patient_email", unique=True)
    db.validator_reports.create_index("patient_email")
    db.validator_reports.create_index("stage")


def seed_defaults() -> dict:
    db = get_db()
    created = 0
    for user in DEFAULT_USERS:
        existing = db.users.find_one({"email": user["email"]})
        if not existing:
            db.users.insert_one({**user, "created_at": datetime.now(timezone.utc)})
            created += 1
    return {"created_users": created, "total_default_users": len(DEFAULT_USERS)}
