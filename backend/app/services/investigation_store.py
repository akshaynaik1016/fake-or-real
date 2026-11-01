"""Durable investigation snapshots; reads never trigger external services."""
from copy import deepcopy
from datetime import timezone
from app.services.assessment_semantics import scan_presentation
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.all_models import Scan, ScanEvidence, VerificationResult, InvestigationState
from app.agents.investigation_orchestrator import investigate


def save_state(db: Session, scan: Scan, payload: dict) -> None:
    record = db.get(InvestigationState, scan.id)
    if record is None:
        db.add(InvestigationState(scan_id=scan.id, revision=payload["revision"], payload=payload))
    else:
        record.payload = deepcopy(payload)
        record.revision = payload["revision"]


async def load_state(db: Session, scan: Scan) -> dict:
    record = db.get(InvestigationState, scan.id)
    if record:
        from app.services.assessment_semantics import integrity_view
        return integrity_view(record.payload)
    # Backfill historical records using retained observations only. No rescanning.
    evs = db.query(ScanEvidence).filter_by(scan_id=scan.id).all()
    checks = db.query(VerificationResult).filter_by(scan_id=scan.id).all()
    evidence = []
    for e in evs:
        evidence.append({"id": e.id, "category": e.category, "severity": e.severity,
            "evidence": e.evidence, "source": e.source, "confidence": e.confidence or 0.5,
            "explanation": e.explanation or "", "timestamp": e.timestamp.isoformat(),
            "origin": "SYNTHETIC" if scan.is_demo else "DETERMINISTIC_RULE",
            "verification_status": "SYNTHETIC" if scan.is_demo else "UNKNOWN"})
    from app.scanners.org_scanner import identify_claimed_organization
    ref = identify_claimed_organization(scan.input_content)
    baseline = {"evidence": evidence, "trust_score": scan.trust_score, "risk_level": scan.risk_level,
        "analysis_confidence": scan.analysis_confidence, "summary": scan.summary,
        "verification_results": [{"check_name": c.check_name, "status": c.status, "details": c.details} for c in checks],
        "timeline": [], "indicators": [], "recommended_actions": ["Verify this historical record independently."],
        "claimed_organization": ref["canonical_name"] if ref else None}
    # No configured language provider or research is invoked during historical reads.
    state = await investigate("", baseline, perform_research=False, use_llm=False)
    state["entities"] = []
    state["language"] = {"provider": "deterministic", "mode": "FALLBACK", "interpretations": [],
                         "claims": [], "reason": "Historical evidence has incomplete provenance"}
    state["coverage_checks"] = [{"name": "Historical provenance", "completed": False,
                                  "reason": "No retained execution metadata; re-submit for a new investigation"}]
    from app.agents.investigation_orchestrator import refresh_investigation
    refresh_investigation(state)
    save_state(db, scan, state)
    db.commit()
    return state


async def scan_response(db: Session, scan_id: str) -> dict:
    scan = db.get(Scan, scan_id)
    if scan is None:
        from app.core.config import settings
        from app.services.demo_seed import get_demo_cases
        case = next((c for c in get_demo_cases() if c["id"] == scan_id), None)
        if not case or not settings.DEMO_MODE:
            raise HTTPException(404, "Scan record not found")
        from app.api.v1.endpoints.analyze import _persist_and_format_scan
        return (await _persist_and_format_scan(db, case["input_type"], case["content"],
            case["target_identifier"], synthetic=True, scan_id=scan_id)).model_dump()
    state = await load_state(db, scan)
    baseline = state["baseline"]
    return {"id": scan.id, "input_type": scan.input_type, "input_content": scan.input_content,
        "target_identifier": scan.target_identifier, "status": scan.status, "trust_score": scan.trust_score,
        "risk_level": scan.risk_level, "analysis_confidence": scan.analysis_confidence, "summary": scan.summary,
        "created_at": scan.created_at.replace(tzinfo=timezone.utc), "is_demo": scan.is_demo,
        "evidence": state["evidence"], "verification_results": baseline.get("verification_results", []),
        "indicators": baseline.get("indicators", []), "recommended_actions": baseline.get("recommended_actions", []),
        "timeline": baseline.get("timeline", []), "threat_intel_details": baseline.get("threat_intel_details"),
        "investigation": state, **scan_presentation(state)}
