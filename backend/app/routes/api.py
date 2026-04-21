from bson.errors import InvalidId
from flask import Blueprint, jsonify, request

from app.services.application_service import get_patient_application, upsert_patient_application
from app.services.report_service import (
    analytics_summary,
    apply_decision,
    approved_claims_summary,
    list_reports,
)
from app.services.seed_service import seed_defaults
from app.utils.db import get_db
from app.utils.serializers import normalize_doc

api_bp = Blueprint("api", __name__)


@api_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@api_bp.post("/seed")
def seed():
    return jsonify(seed_defaults()), 201


@api_bp.post("/auth/login")
def login():
    payload = request.get_json(force=True)
    email = payload.get("email", "").strip().lower()
    password = payload.get("password")
    role = payload.get("role")

    user = get_db().users.find_one({"email": email, "password": password, "role": role})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "user": {
            "email": user["email"],
            "role": user["role"],
            "name": user.get("name", ""),
        },
    })


@api_bp.get("/patients/<path:email>/application")
def patient_application(email: str):
    app_doc = normalize_doc(get_patient_application(email))
    if not app_doc:
        return jsonify({"message": "No application found", "stage": "new"})
    return jsonify(app_doc)


@api_bp.post("/patients/<path:email>/application")
def submit_application(email: str):
    payload = request.get_json(force=True)
    doc = normalize_doc(upsert_patient_application(email, payload))
    return jsonify(doc), 201


@api_bp.get("/reports")
def reports():
    items = [normalize_doc(item) for item in list_reports()]
    return jsonify({"count": len(items), "reports": items})


@api_bp.patch("/reports/<report_id>/decision")
def review_decision(report_id: str):
    payload = request.get_json(force=True)
    decision = payload.get("decision")
    reviewer_email = payload.get("reviewer_email", "validator@med.com")
    if decision not in {"approve", "reject"}:
        return jsonify({"error": "decision must be approve or reject"}), 400

    try:
        doc = apply_decision(report_id, decision, reviewer_email)
    except InvalidId:
        return jsonify({"error": "invalid report id"}), 400

    if not doc:
        return jsonify({"error": "report not found"}), 404
    return jsonify(normalize_doc(doc))


@api_bp.get("/admin/approved-claims")
def admin_claims():
    summary = approved_claims_summary()
    summary["records"] = [normalize_doc(item) for item in summary["records"]]
    return jsonify(summary)


@api_bp.get("/analytics/summary")
def analytics():
    return jsonify(analytics_summary())
