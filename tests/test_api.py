"""
Comprehensive API Integration Test Suite for FAKE OR REAL Platform.
Tests all endpoints: Health, Analyze, Scans, Demo Cases, Emergency Triage,
Trust Passport, Community Reporting, AI Investigator, Reports, and Admin Metrics.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert "UNMASK" in data["platform"]
    assert data["tagline"] == "Don't trust. Verify."

def test_health_and_readiness_endpoints():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "HEALTHY"

    res_ready = client.get("/api/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["ready"] is True

def test_analyze_text_suspicious_internship():
    payload = {
        "input_type": "text",
        "content": (
            "Congratulations! You are selected for Microsoft AI Internship. "
            "Stipend: ₹45,000/month. Please pay ₹999 registration fee via UPI to hr@okaxis. "
            "Submit Aadhaar, PAN card, and Bank IFSC. Website: https://microsoft-careers-india.xyz"
        ),
        "target_identifier": "Microsoft"
    }
    res = client.post("/api/analyze/text", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] == "ELEVATED CONCERN"
    assert data["assessment"]["verification_status"] == "UNRESOLVED"
    assert data["trust_score"] < 40
    assert 0 <= data["analysis_confidence"] <= 100
    assert data["assessment"]["confidence_kind"] == "HEURISTIC_RELIABILITY_INDEX"
    assert len(data["evidence"]) > 0
    assert len(data["verification_results"]) == 9
    assert any("fee" in r.lower() or "payment" in r.lower() for r in data["recommended_actions"])

def test_analyze_url_legitimate():
    payload = {
        "input_type": "url",
        "content": "https://careers.microsoft.com",
        "target_identifier": "Microsoft"
    }
    res = client.post("/api/analyze/url", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["risk_level"] == "UNDETERMINED"
    assert data["trust_score"] is None
    assert data["assessment"]["offer_authenticity"] == "UNRESOLVED"

def test_demo_cases_list_and_run():
    res = client.get("/api/demo/cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) >= 3
    assert any(c["id"] == "demo-fake-msft-internship" for c in cases)

    # Run the fake internship demo case
    run_res = client.post("/api/demo/run/demo-fake-msft-internship")
    assert run_res.status_code == 200
    demo_data = run_res.json()
    assert demo_data["risk_level"] == "ELEVATED CONCERN"
    assert demo_data["is_demo"] is True

def test_emergency_triage_guidance():
    # Test money sent emergency scenario
    res = client.post("/api/emergency/analyze", json={"incident_type": "money_sent"})
    assert res.status_code == 200
    data = res.json()
    assert data["severity"] == "CRITICAL"
    assert len(data["immediate_steps"]) > 0
    assert any("bank" in step["instructions"].lower() or "bank" in step["action"].lower() for step in data["immediate_steps"])

    # Test password entered emergency scenario
    res_pw = client.post("/api/emergency/analyze", json={"incident_type": "password_entered"})
    assert res_pw.status_code == 200
    data_pw = res_pw.json()
    assert any("password" in step["instructions"].lower() or "password" in step["action"].lower() for step in data_pw["immediate_steps"])

def test_trust_passport_generation():
    res = client.get("/api/trust-passport/demo-fake-msft-internship")
    assert res.status_code == 200
    data = res.json()
    assert "scan_id" in data
    assert "trust_score" in data
    assert "qr_code_url" in data

def test_dashboard_metrics():
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "stats" in data
    assert "charts" in data
    assert data["stats"]["opportunities_checked"] > 0

def test_community_reports_flow():
    # 1. Fetch reports
    res = client.get("/api/community/reports")
    assert res.status_code == 200
    initial_reports = res.json()
    assert len(initial_reports) > 0

    # 2. Submit new report
    new_report = {
        "scam_category": "fake_internship",
        "organization_name": "Test Org Impersonator",
        "target_domain": "test-careers-fake.top",
        "description": "Asked for upfront fee via UPI handle for certificate",
        "evidence_text": "Deposit ₹499 to test@upi",
        "upvotes": 1
    }
    submit_res = client.post("/api/community/reports", json=new_report)
    assert submit_res.status_code == 200
    created = submit_res.json()
    assert created["organization_name"] == "Test Org Impersonator"

def test_ai_investigator():
    req = {
        "scan_id": "demo-fake-msft-internship",
        "question": "Why is this Microsoft opportunity suspicious?"
    }
    res = client.post("/api/ai/investigate", json=req)
    assert res.status_code == 200
    data = res.json()
    assert len(data["answer"]) > 10
    assert data["grounded_in_evidence"] is True

def test_report_save_and_retrieve():
    # Save a report for the demo scan
    save_res = client.post("/api/reports/demo-fake-msft-internship/save")
    assert save_res.status_code == 200
    report_data = save_res.json()
    assert "share_token" in report_data
    report_id = report_data["id"]

    # Retrieve the saved report
    get_res = client.get(f"/api/reports/{report_id}")
    assert get_res.status_code == 200
    assert get_res.json()["scan_id"] == "demo-fake-msft-internship"

    # Verify PDF report generation
    pdf_res = client.get("/api/reports/demo-fake-msft-internship/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 100

def test_admin_metrics_and_audit():
    res = client.get("/api/admin/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert "total_scans" in metrics
    assert "active_scoring_weights" in metrics

    logs_res = client.get("/api/admin/audit-logs")
    assert logs_res.status_code == 200
    assert len(logs_res.json()) > 0
