from datetime import datetime, timezone

from bson import ObjectId

from app.utils.db import get_db


def list_reports():
    db = get_db()
    return list(db.validator_reports.find().sort("updated_at", -1))


def apply_decision(report_id: str, decision: str, reviewer_email: str):
    db = get_db()
    report = db.validator_reports.find_one({"_id": ObjectId(report_id)})
    if not report:
        return None

    stage = "approved" if decision == "approve" else "rejected"
    update_fields = {
        "validator_decision": stage,
        "stage": stage,
        "payment_status": "Approved" if stage == "approved" else "Rejected",
        "reviewed_by": reviewer_email,
        "reviewed_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    db.validator_reports.update_one({"_id": report["_id"]}, {"$set": update_fields})
    db.applications.update_one(
        {"patient_email": report["patient_email"]},
        {
            "$set": {
                "stage": stage,
                "payment_status": update_fields["payment_status"],
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return db.validator_reports.find_one({"_id": report["_id"]})


def approved_claims_summary():
    db = get_db()
    approved = list(db.validator_reports.find({"stage": "approved"}))
    total_bill = sum(item.get("bill", {}).get("total", 0) for item in approved)
    insurance = round(total_bill * 0.5)
    patient_pay = total_bill - insurance
    return {
        "approved_count": len(approved),
        "total_bill": total_bill,
        "total_insurance": insurance,
        "total_patient_pay": patient_pay,
        "records": approved,
    }


def analytics_summary():
    db = get_db()
    reports = list(db.validator_reports.find())
    total = len(reports)
    approved = len([r for r in reports if r.get("stage") == "approved"])
    rejected = len([r for r in reports if r.get("stage") == "rejected"])
    pending = total - approved - rejected
    total_bill = sum(item.get("bill", {}).get("total", 0) for item in reports)

    return {
        "total_reports": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
        "total_bill": total_bill,
        "approval_rate": round((approved / total) * 100, 2) if total else 0,
    }
