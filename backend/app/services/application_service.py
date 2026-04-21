from datetime import datetime, UTC

from app.utils.db import get_db


def get_patient_application(email: str):
    db = get_db()
    return db.applications.find_one({"patient_email": email})


def upsert_patient_application(email: str, payload: dict) -> dict:
    db = get_db()
    bill_total = int(payload.get("bill_total", 0))
    doc = {
        "patient_email": email,
        "name": payload.get("name", "Anonymous"),
        "patient_id": payload.get("patient_id") or f"MCP{int(datetime.now(UTC).timestamp())}",
        "age": payload.get("age"),
        "diseases": payload.get("diseases"),
        "income": int(payload.get("income", 0)),
        "hospital_name": payload.get("hospital_name"),
        "doctor_name": payload.get("doctor_name"),
        "bill": {
            "total": bill_total,
            "insurance": round(bill_total * 0.5),
            "patient_pay": bill_total - round(bill_total * 0.5),
        },
        "stage": payload.get("stage", "submitted"),
        "payment_status": payload.get("payment_status", "Pending"),
        "updated_at": datetime.now(UTC),
    }

    existing = db.applications.find_one({"patient_email": email})
    if existing:
        db.applications.update_one({"patient_email": email}, {"$set": doc})
    else:
        doc["created_at"] = datetime.now(UTC)
        db.applications.insert_one(doc)

    report_doc = {
        "patient_email": email,
        "patient_id": doc["patient_id"],
        "name": doc["name"],
        "age": doc["age"],
        "diseases": doc["diseases"],
        "income": doc["income"],
        "hospital_name": doc["hospital_name"],
        "doctor_name": doc["doctor_name"],
        "bill": doc["bill"],
        "stage": doc["stage"],
        "validator_decision": None,
        "updated_at": datetime.now(UTC),
    }
    db.validator_reports.update_one({"patient_email": email}, {"$set": report_doc}, upsert=True)
    return doc
