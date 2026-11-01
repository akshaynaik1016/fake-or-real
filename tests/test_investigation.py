import asyncio
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.all_models import InvestigationState, InvestigationExecution, Scan, User
from app.services.evidence_service import normalize_evidence
from app.services.bayesian_evidence_engine import FusionConfig, fuse_evidence
from app.services.trust_graph_service import build_trust_graph
from app.agents.investigation_orchestrator import extract_entities
from app.integrations.web_research.tavily_service import TavilyService, safe_source_url
from app.integrations.llm.provider import explain, register_provider
from app.schemas.investigation import LanguageOutput

client = TestClient(app)
OFFER = ("From: Microsoft Careers <recruiter@unverified.example.com>\n\n"
         "Microsoft internship. Pay ₹999 registration fee via UPI to hiring@okaxis. "
         "Upload Aadhaar and PAN card. Act immediately within 30 minutes. "
         "https://microsoft-careers-india.xyz")


def ev(category="payment_risk", severity="high", **kwargs):
    return normalize_evidence([dict(category=category, severity=severity, evidence="Pay ₹999",
        source="Submitted content rule", confidence=1, observed_value="Pay ₹999", **kwargs)])[0]


def submit(content=OFFER):
    response = client.post("/api/analyze/text", json={"input_type": "text", "content": content})
    assert response.status_code == 200, response.text
    return response.json()


def test_empty_evidence_has_no_safe_verdict_or_confidence_floor():
    r = fuse_evidence([], [{"name": "Research", "completed": False}])
    assert r["risk_level"] == "UNDETERMINED"
    assert r["risk_score"] is None
    assert r["confidence"] == r["evidence_coverage"] == 0
    assert r["unknowns"]


def test_correlated_findings_contribute_only_once_and_order_does_not_change_score():
    a = ev("domain_age", "high")
    b = ev("dns_records", "moderate")
    result = fuse_evidence([a, b], [])
    assert sum(u["included"] for u in result["evidence_updates"]) == 1
    assert result["risk_score"] == fuse_evidence([a], [])["risk_score"]
    assert result["risk_score"] == fuse_evidence([b, a], [])["risk_score"]


def test_identical_evidence_ids_never_count_twice():
    a = ev()
    single = fuse_evidence([a], [])
    repeated = fuse_evidence([a, a], [])
    assert repeated == single


def test_oversized_utf8_password_rejected_before_hashing():
    response = client.post("/api/auth/register", json={"email": "long-password@example.com", "password": "界" * 25})
    assert response.status_code == 422


def test_payment_language_and_payment_scanner_are_correlated():
    a, b = ev("scam_language_payment_pressure", "critical"), ev("payment_risk", "critical")
    assert a["correlation_group"] == b["correlation_group"]
    assert sum(u["included"] for u in fuse_evidence([a, b], [])["evidence_updates"]) == 1


def test_calibrated_bayes_uses_explicit_prior_likelihood_and_reference():
    config = FusionConfig(prior=0.2, likelihood_ratios={"payment_risk": 4}, calibration_reference="test-only-fixture")
    result = fuse_evidence([ev()], [], config)
    assert result["assessment_mode"] == "BAYESIAN"
    assert result["risk_score"] == 50
    assert result["evidence_updates"][0]["likelihood_ratio"] == 4


@pytest.mark.parametrize("kwargs", [{"prior": 0}, {"prior": 1},
    {"likelihood_ratios": {"payment_risk": 4}},
    {"likelihood_ratios": {"payment_risk": -1}, "calibration_reference": "test"}])
def test_invalid_fusion_config_rejected(kwargs):
    with pytest.raises(ValueError):
        FusionConfig(**kwargs)


def test_partial_calibration_never_masquerades_as_bayesian():
    config = FusionConfig(likelihood_ratios={"other": 4}, calibration_reference="test")
    assert fuse_evidence([ev()], [], config)["assessment_mode"] == "HEURISTIC"


def test_contradictory_observations_retained_and_reduce_confidence():
    a = ev("identity_match", "critical")
    b = ev("organization_verification", "verified")
    r = fuse_evidence([a, b], [])
    assert b["id"] in r["contradicting_evidence"]
    assert r["confidence"] < fuse_evidence([a], [])["confidence"]
    assert any("Conflicting" in u for u in r["unknowns"])


@pytest.mark.parametrize("origin", ["SYNTHETIC", "EXTERNAL_SOURCE", "AI_INTERPRETATION"])
def test_unverified_or_interpretive_evidence_cannot_set_risk(origin):
    evidence = ev()
    evidence["origin"] = origin
    assert fuse_evidence([evidence], [])["risk_score"] is None


def test_provenance_stable_ids_redaction_and_original_observation():
    a = normalize_evidence([{
        "category": "sensitive_data", "severity": "critical", "source": "User content", "evidence": "OTP is 984712",
        "observed_value": "OTP is 984712", "confidence": 0.8}])[0]
    assert "984712" not in json.dumps(a)
    assert a["id"] == normalize_evidence([a])[0]["id"]
    assert a["timestamp"] and a["observed_value"]


def test_graph_edges_only_reference_real_nodes_and_related_entities():
    entities = extract_entities(OFFER, "Microsoft")
    row = ev()
    row["related_entities"] = [entities[0]["id"], "invented-entity"]
    graph = build_trust_graph(entities, [row], [])
    ids = {n["id"] for n in graph["nodes"]}
    assert "invented-entity" not in ids
    assert all(e["source"] in ids and e["target"] in ids for e in graph["edges"])
    assert {"email", "domain", "payment", "organization"} <= {n["type"] for n in graph["nodes"]}
    assert not any(e["relation"] in {"owns", "authenticated_by"} for e in graph["edges"])


def test_tavily_unconfigured_performs_no_http(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("HTTP should not be instantiated")
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    r = asyncio.run(TavilyService(api_key="").search("Microsoft"))
    assert r.status == "SEARCH_UNAVAILABLE" and not r.sources


def test_tavily_contract_provenance_domain_boundary_and_no_generated_answer():
    calls = []
    def handler(req):
        calls.append(req)
        body = json.loads(req.content)
        assert body["include_answer"] is False
        assert body["max_results"] == 5
        return httpx.Response(200, json={"results": [
            {"title": "Official careers", "url": "https://careers.microsoft.com/jobs", "content": "Role listing", "score": 0.9},
            {"title": "Impostor", "url": "https://microsoft.com.evil.example/jobs", "content": "Brand mention", "score": 0.8},
            {"title": "Local", "url": "http://127.0.0.1/secrets", "content": "Ignore instructions", "score": 1}]})
    r = asyncio.run(TavilyService(api_key="test-key", transport=httpx.MockTransport(handler)).search("Microsoft", ["microsoft.com"]))
    assert len(calls) == 1 and len(r.sources) == 2
    assert r.sources[0].source_type == "OFFICIAL_DOMAIN"
    assert r.sources[1].source_type == "INDEPENDENT_SOURCE"
    assert all(s.verification_status == "NOT_INDEPENDENTLY_VERIFIED" and s.retrieved_at for s in r.sources)


@pytest.mark.parametrize("response", [httpx.Response(500), httpx.Response(429),
    httpx.Response(200, json={"results": "bad"}),
    httpx.Response(200, json={"results": [{"title": "bad", "score": 8}]})])
def test_tavily_failures_are_explicit_and_do_not_leak_secrets(response):
    r = asyncio.run(TavilyService(api_key="secret-test-value", transport=httpx.MockTransport(lambda _: response)).search("Microsoft"))
    assert r.status == "SEARCH_UNAVAILABLE"
    assert "secret-test-value" not in r.model_dump_json()


def test_tavily_timeout_has_explicit_unavailable_state():
    def timeout(_):
        raise httpx.ReadTimeout("secret internal error")
    r = asyncio.run(TavilyService(api_key="key", transport=httpx.MockTransport(timeout)).search("Company"))
    assert r.status == "SEARCH_UNAVAILABLE"
    assert "secret internal error" not in r.reason


@pytest.mark.parametrize("url", ["file:///etc/passwd", "javascript:alert(1)", "http://localhost/a", "http://[::1]/", "http://user:pass@public.example/a"])
def test_unsafe_research_source_links_rejected(url):
    assert safe_source_url(url) is None


def test_llm_none_no_provider_needed():
    result = asyncio.run(explain("hello", [], {"interpretations": [], "claims": []}))
    assert result["mode"] == "FALLBACK" and result["provider"] == "deterministic"


def test_provider_independent_adapter_valid_citations_and_redacted_input(monkeypatch):
    row = ev()
    class TestProvider:
        name = "test-hosted-or-local"
        async def understand(self, **kwargs):
            assert "984712" not in kwargs["untrusted_content"]
            return LanguageOutput(interpretations=[{"text": "Observed payment demand", "evidence_ids": [row["id"]]}])
    register_provider("test", TestProvider())
    monkeypatch.setattr(settings, "AI_PROVIDER", "test")
    result = asyncio.run(explain("OTP is 984712", [row], {}))
    assert result["mode"] == "LLM_INTERPRETATION"
    assert result["verification_status"] == "AI_GENERATED_NOT_INDEPENDENTLY_VERIFIED"


@pytest.mark.parametrize("output", [
    {"risk_score": 0, "interpretations": []},
    {"interpretations": [{"text": "Invented", "evidence_ids": ["unknown"]}]},
    {"interpretations": [{"text": "Payment", "evidence_ids": ["placeholder"]}],
     "claims": [{"text": "Microsoft endorses it", "quote": "fabricated quote"}]}])
def test_invalid_language_output_falls_back_without_touching_evidence(monkeypatch, output):
    row = ev()
    output = json.loads(json.dumps(output).replace('placeholder', row["id"]))
    class BadProvider:
        name = "bad-test"
        async def understand(self, **kwargs):
            kwargs["evidence"].clear()
            return output
    register_provider("bad", BadProvider())
    monkeypatch.setattr(settings, "AI_PROVIDER", "bad")
    original = deepcopy(row)
    result = asyncio.run(explain("Real submitted text", [row], {"interpretations": []}))
    assert result["mode"] == "FALLBACK" and row == original


def test_language_timeout_falls_back(monkeypatch):
    class Slow:
        name = "slow"
        async def understand(self, **kwargs):
            await asyncio.sleep(1)
    register_provider("slow", Slow())
    monkeypatch.setattr(settings, "AI_PROVIDER", "slow")
    monkeypatch.setattr(settings, "LLM_TIMEOUT_SECONDS", 0.001)
    assert asyncio.run(explain("x", [ev()], {}))["mode"] == "FALLBACK"


def test_complete_offline_workflow_no_network_and_persisted_reads(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline workflow attempted HTTP")
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    result = submit()
    state = result["investigation"]
    assert state["language"]["provider"] == "deterministic"
    assert state["research"][0]["status"] == "SEARCH_UNAVAILABLE"
    assert state["fusion"]["assessment_mode"] == "HEURISTIC"
    assert state["fusion"]["risk_level"] in {"HIGH", "CRITICAL"}
    assert 0 < state["fusion"]["evidence_coverage"] < 100
    assert all(e["id"] and e["timestamp"] and e["observed_value"] for e in state["evidence"])
    import app.services.scan_service as scan_service
    monkeypatch.setattr(scan_service, "execute_full_scan", AsyncMock(side_effect=AssertionError("Reads must not rescan")))
    reloaded = client.get(f"/api/scans/{result['id']}").json()
    assert reloaded["investigation"] == state
    assert client.get(f"/api/investigations/{result['id']}/graph").json() == state["graph"]
    report = client.get(f"/api/reports/{result['id']}/pdf")
    assert report.status_code == 200 and report.content.startswith(b"%PDF")
    answer = client.post("/api/ai/investigate", json={"scan_id": result["id"], "question": "Why suspicious?"}).json()
    assert answer["mode"] == "FALLBACK" and answer["evidence_ids"]


def test_automated_investigation_updates_snapshot_history_and_graph():
    result = submit()
    sid = result["id"]
    state = result["investigation"]
    action = next(a for a in state["recommendations"] if a["action_id"] == "verify_sender_domain")
    assert action["status"] == "AVAILABLE" and action["priority"] == "HIGH"
    path = f"/api/investigations/{sid}/actions/verify_sender_domain"
    response = client.post(path, json={"expected_revision": state["revision"]})
    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["revision"] == 2
    assert updated["history"][-1]["status"] == "COMPLETED"
    assert len(updated["evidence"]) > len(state["evidence"])
    assert len(updated["graph"]["nodes"]) > len(state["graph"]["nodes"])
    assert updated["last_change"]["after"] == updated["fusion"]
    assert client.get(f"/api/scans/{sid}").json()["investigation"] == updated
    assert client.get(f"/api/trust-passport/{sid}").json()["evidence_count"] == len(updated["evidence"])
    assert client.post(path, json={"expected_revision": 1}).status_code == 409
    assert client.post(path, json={"expected_revision": 2}).json() == updated
    with SessionLocal() as db:
        assert db.query(InvestigationExecution).filter_by(scan_id=sid).count() == 1


def test_manual_unknown_and_unavailable_actions_cannot_execute():
    result = submit()
    base = f"/api/investigations/{result['id']}/actions/"
    for action, code in [("contact_organization", 400), ("arbitrary_tool", 400), ("research_warnings", 409)]:
        assert client.post(base + action, json={"expected_revision": 1}).status_code == code


def test_bounded_research_updates_sources_but_not_risk(monkeypatch):
    from app.schemas.investigation import ResearchResult, ResearchSource
    calls = []
    async def search(self, query, official_domains=None):
        calls.append(query)
        return ResearchResult(status="COMPLETED", query=query, sources=[ResearchSource(
            id="source-1", title="Careers", url="https://www.microsoft.com/careers", extracted_information="Company exists",
            retrieved_at="2026-11-01T00:00:00Z", source_type="OFFICIAL_DOMAIN", relevance=0.9, claim=query)])
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "test")
    monkeypatch.setattr(TavilyService, "search", search)
    result = submit()
    initial = result["investigation"]
    assert initial["research_calls"] == 1
    assert any(e["origin"] == "EXTERNAL_SOURCE" for e in initial["evidence"])
    updated = client.post(f"/api/investigations/{result['id']}/actions/research_warnings", json={"expected_revision": 1}).json()
    assert updated["research_calls"] == 2 and len(calls) == 2
    assert updated["fusion"]["risk_score"] == initial["fusion"]["risk_score"]
    assert all(s["verification_status"] == "NOT_INDEPENDENTLY_VERIFIED" for r in updated["research"] for s in r["sources"])


def test_failed_research_attempts_exhaust_budget_without_unlimited_retries(monkeypatch):
    from app.schemas.investigation import ResearchResult
    calls = []
    async def unavailable(self, query, official_domains=None):
        calls.append(query)
        return ResearchResult(status="SEARCH_UNAVAILABLE", query=query, reason="Test provider unavailable")
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "test")
    monkeypatch.setattr(TavilyService, "search", unavailable)
    result = submit()
    path = f"/api/investigations/{result['id']}/actions/research_warnings"
    for revision in (1, 2):
        response = client.post(path, json={"expected_revision": revision})
        assert response.status_code == 200, response.text
    state = response.json()
    assert state["research_calls"] == len(calls) == 3
    assert client.post(path, json={"expected_revision": 3}).status_code == 409
    assert len(calls) == 3


def test_unknown_scan_never_returns_invented_demo():
    assert client.post("/api/ai/investigate", json={"scan_id": "missing", "question": "why"}).status_code == 404
    assert client.get("/api/trust-passport/missing").status_code == 404
    assert client.post("/api/demo/run/missing").status_code == 404


def test_synthetic_fixture_sources_are_explicit_and_excluded():
    result = client.post("/api/demo/run/demo-fake-msft-internship").json()
    assert result["is_demo"]
    synthetic = {e["id"] for e in result["investigation"]["evidence"] if e["origin"] == "SYNTHETIC"}
    assert synthetic
    assert all(not u["included"] for u in result["investigation"]["fusion"]["evidence_updates"] if u["evidence_id"] in synthetic)
    assert any(a["action_id"] == "verify_sender_domain" for a in result["investigation"]["recommendations"])


def test_salary_or_negated_fee_is_not_a_payment_demand():
    from app.scanners.payment_scanner import analyze_payment_risk
    assert not analyze_payment_risk("Stipend ₹45,000/month, apply with resume")["payment_detected"]
    assert not analyze_payment_risk("There is no registration fee or security deposit")["payment_detected"]
    assert analyze_payment_risk("Pay ₹999 registration fee")["payment_detected"]
    from app.scanners.text_scanner import analyze_scam_language
    assert not analyze_scam_language("There is no registration fee or security deposit")["has_payment_pressure"]


def test_malicious_language_output_cannot_change_core_assessment(monkeypatch):
    baseline = submit()["investigation"]["fusion"]
    class ScoreSetter:
        name = "untrusted-score-setter"
        async def understand(self, **kwargs):
            return {"risk_score": 0, "evidence": [{"evidence": "fabricated endorsement"}]}
    register_provider("score-setter", ScoreSetter())
    monkeypatch.setattr(settings, "AI_PROVIDER", "score-setter")
    updated = submit()["investigation"]
    assert updated["language"]["mode"] == "FALLBACK"
    assert updated["fusion"]["risk_score"] == baseline["risk_score"]
    assert not any(e["evidence"] == "fabricated endorsement" for e in updated["evidence"])


def test_tls_connects_only_to_prevalidated_ip(monkeypatch):
    import app.scanners.ssl_scanner as scanner
    monkeypatch.setattr(settings, "NETWORK_SCANNERS_ENABLED", True)
    monkeypatch.setattr(scanner, "validate_and_resolve_url", lambda *_: (True, "https://example.com", ["93.184.216.34"]))
    destinations = []
    def connect(destination, timeout):
        destinations.append(destination)
        raise OSError("Test ends before opening a socket")
    monkeypatch.setattr(scanner.socket, "create_connection", connect)
    scanner.analyze_ssl_certificate("example.com")
    assert destinations == [("93.184.216.34", 443)]


def test_tls_unresolved_destination_cannot_connect(monkeypatch):
    import app.scanners.ssl_scanner as scanner
    monkeypatch.setattr(settings, "NETWORK_SCANNERS_ENABLED", True)
    monkeypatch.setattr(scanner, "validate_and_resolve_url", lambda *_: (True, "https://example.com", []))
    def forbidden(*args, **kwargs):
        raise AssertionError("Unvalidated destination must not connect")
    monkeypatch.setattr(scanner.socket, "create_connection", forbidden)
    assert scanner.analyze_ssl_certificate("example.com")["status"] == "UNAVAILABLE"


def test_tavily_redirect_not_followed():
    calls = []
    def redirect(req):
        calls.append(req)
        return httpx.Response(302, headers={"location": "http://127.0.0.1/secrets"})
    result = asyncio.run(TavilyService(api_key="test", transport=httpx.MockTransport(redirect)).search("Company"))
    assert result.status == "SEARCH_UNAVAILABLE" and len(calls) == 1


def test_synthetic_summary_excludes_fixture_claims():
    result = client.post("/api/demo/run/demo-fake-msft-internship").json()["investigation"]
    synthetic = {e["id"] for e in result["evidence"] if e["origin"] == "SYNTHETIC"}
    assert all(e["evidence"].startswith("[Synthetic fixture]") for e in result["evidence"] if e["id"] in synthetic)
    assert not synthetic.intersection(id for s in result["language"]["interpretations"] for id in s["evidence_ids"])


def test_failed_ocr_does_not_invent_offer_text(monkeypatch):
    import pytesseract
    from app.ocr.ocr_engine import extract_text_from_image
    monkeypatch.setattr(pytesseract, "image_to_string", lambda *a, **k: "")
    r = extract_text_from_image(b"invalid", "internship-offer.png")
    assert r["extracted_text"] == "" and r["bounding_boxes"] == [] and r["status"] == "UNAVAILABLE"


def test_webp_requires_actual_webp_signature():
    from app.security.file_validator import validate_uploaded_file
    assert not validate_uploaded_file(b"RIFF0000WAVEfake", "test.webp")[0]


def test_no_fabricated_domain_registration_age():
    from app.scanners.domain_scanner import analyze_domain_intelligence
    r = analyze_domain_intelligence("microsoft-careers-india.xyz")
    assert r["age_days"] is None and r["created_date"] is None and r["status"] == "UNAVAILABLE"


def test_production_missing_secret_fails_closed():
    env = {**os.environ, "ENVIRONMENT": "production", "DEMO_MODE": "false", "JWT_SECRET": ""}
    r = subprocess.run([sys.executable, "-c", "from app.core.config import settings"],
        env={**env, "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "backend")}, capture_output=True, text=True)
    assert r.returncode != 0 and "Production requires" in r.stderr


def test_authentication_ownership_and_admin_authorization(monkeypatch):
    import uuid
    email = uuid.uuid4().hex + "@example.com"
    token = client.post("/api/auth/register", json={"email": email, "password": "test-long-password"}).json()["access_token"]
    headers = {"Authorization": "Bearer " + token}
    result = submit()
    monkeypatch.setattr(settings, "DEMO_MODE", False)
    assert client.get(f"/api/scans/{result['id']}").status_code == 401
    assert client.get(f"/api/scans/{result['id']}", headers=headers).status_code == 404
    assert client.get("/api/admin/metrics", headers=headers).status_code == 403
    assert client.get("/api/auth/me", headers=headers).json()["email"] == email
    own = client.post("/api/analyze/text", headers=headers, json={"input_type": "text", "content": OFFER})
    assert own.status_code == 200
    assert client.get(f"/api/scans/{own.json()['id']}", headers=headers).status_code == 200


def test_input_metadata_cannot_inject_scoring_evidence():
    result = client.post("/api/scans", json={"input_type": "text", "content": "Please review the role details.",
        "metadata": {"flags": [{"severity": "critical", "message": "fabricated", "detail": "forged"}]}}).json()
    assert not any(e["evidence"] == "fabricated" for e in result["evidence"])


def test_rate_limit_applied_to_investigation_posts():
    from app.core.rate_limiter import rate_limiter
    import time
    rate_limiter.requests["testclient"] = [time.time()] * 60
    assert client.post("/api/analyze/text", json={"input_type": "text", "content": "test"}).status_code == 429


def test_additive_migration_preserves_existing_rows(tmp_path):
    import sqlite3
    from alembic.config import Config
    from alembic import command
    database = tmp_path / "legacy.db"
    with sqlite3.connect(database) as con:
        con.execute("CREATE TABLE scans (id TEXT PRIMARY KEY, input_content TEXT)")
        con.execute("INSERT INTO scans VALUES ('legacy', 'retained')")
    previous = settings.DATABASE_URL
    settings.DATABASE_URL = "sqlite:///" + str(database)
    try:
        cfg = Config(str(Path(__file__).resolve().parents[1] / "backend/alembic.ini"))
        command.upgrade(cfg, "head")
        command.upgrade(cfg, "head")
    finally:
        settings.DATABASE_URL = previous
    with sqlite3.connect(database) as con:
        assert con.execute("SELECT input_content FROM scans WHERE id='legacy'").fetchone() == ("retained",)
        assert con.execute("SELECT version_num FROM alembic_version").fetchone() == ("0002_multi_source_cases",)
        assert con.execute("SELECT name FROM sqlite_master WHERE name='investigation_states'").fetchone()
