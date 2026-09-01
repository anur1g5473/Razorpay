"""Comprehensive unit and integration tests for DisputeShield FastAPI endpoints."""

from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "DisputeShield API"
    assert data["status"] == "ok"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_list_cases():
    response = client.get("/api/cases")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 100
    assert len(data["cases"]) == 100
    assert "fraudulent_unauthorized" in data["categories"]
    assert "win" in data["outcomes"]
    assert "lose" in data["outcomes"]
    assert "ambiguous" in data["outcomes"]


def test_filter_cases_by_category():
    response = client.get("/api/cases?category=product_service_not_received")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 20
    for case in data["cases"]:
        assert case["dispute_category"] == "product_service_not_received"


def test_filter_cases_by_outcome():
    response = client.get("/api/cases?expected_outcome=win")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 40
    for case in data["cases"]:
        assert case["ground_truth"] == "win"


def test_search_cases():
    response = client.get("/api/cases?search=fraud")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] > 0


def test_get_case_by_id():
    response = client.get("/api/cases/disp_001")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "disp_001"
    assert data["dispute_category"] == "fraudulent_unauthorized"
    assert "dispute_amount" in data or "payment_id" in data


def test_get_case_not_found():
    response = client.get("/api/cases/non_existent_dispute_12345")
    assert response.status_code == 404


def test_analyze_case_win():
    response = client.post("/api/analyze/disp_001")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "disp_001"
    assert data["decision"] == "CONTEST"
    assert data["win_probability_estimate"] >= 0.75
    assert len(data["rebuttal_letter"]) > 100


def test_analyze_case_lose():
    response = client.post("/api/analyze/disp_009")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "disp_009"
    assert data["decision"] in ["ABSTAIN", "ACCEPT", "ACCEPT_CHARGEBACK"]
    assert data["win_probability_estimate"] < 0.50


def test_analyze_case_ambiguous():
    response = client.post("/api/analyze/disp_017")
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "disp_017"
    assert data["decision"] in ["REVIEW", "MANUAL_REVIEW", "CONTEST", "ABSTAIN", "ACCEPT", "ACCEPT_CHARGEBACK"]


def test_analyze_custom_dispute():
    payload = {
        "dispute_category": "product_service_not_received",
        "reason_code": "13.1",
        "dispute_amount": 4500.0,
        "merchant_name": "QuickMart Electronics",
        "evidence_slices": {
            "proof_of_delivery": {
                "carrier_name": "BlueDart",
                "tracking_number": "BD9928192",
                "delivery_timestamp": "2026-08-20T14:30:00Z",
                "delivery_status": "Delivered",
                "recipient_signature_or_gps": "GPS: 19.0760, 72.8777 (Exact match)",
            },
            "fulfillment_dispatch_proof": {
                "invoice_number": "INV-2026-9912",
                "dispatch_date": "2026-08-18",
                "item_manifest": "Sony WH-1000XM5 Headphones",
            },
        },
    }
    response = client.post("/api/analyze/custom/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["dispute_category"] == "product_service_not_received"
    assert data["decision"] in ["CONTEST", "REVIEW", "MANUAL_REVIEW"]
    assert len(data["rebuttal_letter"]) > 100


def test_get_rubric():
    response = client.get("/api/rubric")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == 6


def test_get_rubric_categories():
    response = client.get("/api/rubric/categories")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert len(data["categories"]) == 6


def test_get_rubric_by_reason_code():
    response = client.get("/api/rubric/10.4")
    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == "fraudulent_unauthorized"


def test_eval_results_and_summary():
    # Summary endpoint
    res_summary = client.get("/api/eval/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["overall_accuracy"] >= 0.85
    assert summary["dispute_prevention_savings_inr"] > 0

    # Results endpoint
    res_results = client.get("/api/eval/results")
    assert res_results.status_code == 200
    results = res_results.json()
    assert results["total_cases"] >= 30


