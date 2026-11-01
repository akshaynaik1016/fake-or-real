"""
Scanner and Forensic Layer Test Suite for FAKE OR REAL
Tests URL dissection, registrable domain resolution, text scam indicators,
payment risk detection, and sensitive data extraction.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.scanners.url_scanner import analyze_url_structure
from app.scanners.text_scanner import scan_text_patterns
from app.scanners.payment_scanner import scan_payment_risks
from app.scanners.sensitive_data_scanner import scan_sensitive_data
from app.scanners.org_scanner import verify_organization_match


def test_url_registrable_domain_isolation():
    """Verify subdomain spoofing like google.com.security-check.example.xyz identifies example.xyz as the true domain."""
    res = analyze_url_structure("https://google.com.security-check.example.xyz/login")
    assert res["registrable_domain"] == "example.xyz"
    assert res["excessive_subdomains"] is True
    # Verify indicator found
    indicators = [ind["indicator"] for ind in res["indicators"]]
    assert any("Lookalike Brand" in ind or "Excessive Subdomains" in ind for ind in indicators)


def test_url_entropy_and_tld_flag():
    """Verify high-entropy random string URLs and risky TLDs are flagged."""
    res = analyze_url_structure("http://xj823lka9q018bzk1.top/verify")
    indicators = [ind["indicator"] for ind in res["indicators"]]
    assert any("Suspicious TLD" in ind for ind in indicators)
    assert res["is_https"] is False


def test_text_scam_urgency_and_manipulation():
    """Verify detection of urgency, guaranteed income, and emotional pressure."""
    text = "Congratulations! You are specially selected. Offer expires today! Act immediately within 30 minutes to secure your seat."
    res = scan_text_patterns(text)
    assert res["urgency_detected"] is True
    assert res["manipulation_detected"] is True
    assert len(res["matched_categories"]) >= 2


def test_payment_risk_upfront_fee_and_upi():
    """Verify upfront registration fees and UPI handles are detected with nuanced explanation."""
    text = "Please deposit a refundable security deposit of ₹1,499 via UPI to recruit-hr@okaxis before joining."
    res = scan_payment_risks(text)
    assert res["payment_detected"] is True
    assert len(res["amounts_detected"]) > 0
    assert any("₹1,499" in amt["raw"] or "1,499" in amt["raw"] or "1499" in amt["raw"] for amt in res["amounts_detected"])
    assert len(res["upi_handles"]) > 0
    assert "recruit-hr@okaxis" in res["upi_handles"]


def test_sensitive_data_classification():
    """Verify sensitive data classification across LOW, MEDIUM, CRITICAL tiers."""
    text = "Submit your resume along with Aadhaar card, PAN card, and banking details with your ATM card CVV."
    res = scan_sensitive_data(text)
    assert res["has_sensitive_requests"] is True
    severities = [req["severity"] for req in res["detected_requests"]]
    assert "CRITICAL" in severities  # CVV
    assert "MEDIUM" in severities    # Aadhaar, PAN
    assert "LOW" in severities       # Resume


def test_organization_identity_mismatch():
    """Verify brand claims like 'Microsoft' with an unauthorized domain yield critical identity mismatch."""
    res = verify_organization_match("Microsoft", "microsoft-careers-india.xyz")
    assert res["status"] == "CRITICAL_MISMATCH"
    assert res["claimed_org"] == "Microsoft"
    assert "official domain" in res["explanation"].lower() or "mismatch" in res["explanation"].lower()


def test_organization_identity_verified():
    """Verify legitimate organization domains return VERIFIED status."""
    res = verify_organization_match("Microsoft", "careers.microsoft.com")
    assert res["status"] == "VERIFIED"
    assert res["is_official"] is True
