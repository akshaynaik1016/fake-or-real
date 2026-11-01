from copy import deepcopy
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import update
from app.core.config import settings
from app.models.all_models import InvestigationState, InvestigationExecution
from app.services.investigation_store import load_state
from app.agents.investigation_orchestrator import refresh_investigation, organization_reference
from app.services.evidence_service import normalize_evidence, deterministic_summary
from app.integrations.web_research.tavily_service import TavilyService


async def execute_recommendation(db, scan, action_id: str, expected_revision: int) -> dict:
    state = await load_state(db, scan)
    if state["revision"] != expected_revision:
        raise HTTPException(409, "Investigation changed; reload before executing")
    if any(h.get("status") == "RUNNING" for h in state["history"]):
        raise HTTPException(409, "An investigation action is already running")
    action = next((a for a in state["recommendations"] if a["action_id"] == action_id), None)
    if action is None or action["execution_type"] != "AUTOMATED":
        raise HTTPException(400, "Only a recommended automated action can be executed")
    if action["status"] == "COMPLETED":
        return state
    if action["status"] != "AVAILABLE":
        raise HTTPException(409, action.get("unavailable_reason") or "Investigation action unavailable")
    # Reserve the revision before awaiting a provider. Concurrent workers cannot
    # spend the same budget or overwrite one another's evidence.
    reserved = deepcopy(state)
    reserved["revision"] += 1
    reserved["history"].append({"action_id": action_id, "status": "RUNNING",
        "timestamp": datetime.now(timezone.utc).isoformat()})
    if action_id == "research_warnings":
        if state["research_calls"] >= settings.MAX_RESEARCH_CALLS:
            raise HTTPException(409, "Search budget exhausted")
        reserved["research_calls"] += 1
    changed = db.execute(update(InvestigationState).where(
        InvestigationState.scan_id == scan.id, InvestigationState.revision == expected_revision
    ).values(revision=reserved["revision"], payload=reserved))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Investigation changed; reload")
    db.commit()
    db.expire_all()
    state = reserved
    before = deepcopy(state["fusion"])
    status = "COMPLETED"
    details = ""
    if action_id == "verify_sender_domain":
        org = organization_reference(state["claimed_organization"])
        email = next((e for e in state["entities"] if e["type"] == "email"), None)
        if not org or not email:
            status, details = "UNAVAILABLE", "No organization reference or sender address available"
        else:
            domain = email["value"].split("@")[-1].lower()
            official = [d for d in org["official_domains"] if "/" not in d]
            match = any(domain == d or domain.endswith("." + d) for d in official)
            details = f"Submitted sender domain {domain} {'matches' if match else 'does not match'} bundled organization reference. Sender authorization is still unknown."
            new = normalize_evidence([{"category": "identity_match", "severity": "verified" if match else "high",
                "evidence": details, "explanation": "Reference comparison only; not a live registry query or sender authentication.",
                "source": "Bundled organization domain reference", "confidence": 0.85,
                "observed_value": email["value"], "related_entities": [email["id"]],
                "verification_status": "REFERENCE_MATCH" if match else "REFERENCE_MISMATCH"}])
            state["evidence"] = normalize_evidence(state["evidence"] + new)
    elif action_id == "research_warnings":
        result = await TavilyService().search(
            f'{state["claimed_organization"][:100]} recruitment internship payment scam warnings', state["official_domains"])
        state["research"].append(result.model_dump())
        status = "COMPLETED" if result.status == "COMPLETED" else "UNAVAILABLE"
        details = result.reason
        for check in state["coverage_checks"]:
            if check["name"] == "Independent research" and result.status == "COMPLETED":
                check["completed"] = True
    else:
        raise HTTPException(400, "Unsupported action")
    if action_id == "verify_sender_domain" and status == "COMPLETED":
        for check in state["baseline"].get("verification_results", []):
            if check["check_name"] == "Email":
                check.update(status="warning" if match else "failed", details=details)
    state["history"][-1].update(status=status, details=details)
    # New facts use deterministic explanation; never retain a stale model summary.
    state["language"] = {"provider": "deterministic", "mode": "FALLBACK", "claims": [],
        "reason": "Investigation updated using recorded evidence",
        **deterministic_summary(state["evidence"], 8)}
    refresh_investigation(state)
    state["last_change"] = {"action_id": action_id, "before": before, "after": state["fusion"],
        "reason": details, "risk_score_changed": before["risk_score"] != state["fusion"]["risk_score"],
        "status":status}
    changed = db.execute(update(InvestigationState).where(
        InvestigationState.scan_id == scan.id, InvestigationState.revision == state["revision"]
    ).values(payload=state))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "Investigation updated concurrently")
    db.add(InvestigationExecution(scan_id=scan.id, action_id=action_id,
        revision=state["revision"], result=state["last_change"]))
    db.commit()
    return state
