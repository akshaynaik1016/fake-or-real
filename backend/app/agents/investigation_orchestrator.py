"""Explicit, bounded workflow. No LLM tool selection or model dependency."""
import re
from urllib.parse import urlsplit
from app.core.config import settings
from app.scanners.org_scanner import identify_claimed_organization, VERIFIED_ORGANIZATIONS_REGISTRY
from app.scanners.email_scanner import analyze_email_security
from app.scanners.payment_scanner import analyze_payment_risk
from app.services.evidence_service import normalize_evidence, deterministic_summary
from app.services.bayesian_evidence_engine import fuse_evidence
from app.services.trust_graph_service import build_trust_graph, entity_id
from app.services.next_best_investigation import recommend
from app.integrations.web_research.tavily_service import TavilyService
from app.integrations.llm.provider import explain
from app.schemas.investigation import ResearchResult
from app.security.redaction import redact_sensitive_credentials


def organization_reference(claimed: str | None) -> dict | None:
    if not claimed:
        return None
    for key, org in VERIFIED_ORGANIZATIONS_REGISTRY.items():
        if claimed.lower() == org["canonical_name"].lower() or claimed.lower() in org["aliases"] or claimed.lower() == key:
            return org
    return None


def extract_entities(content: str, claimed_org: str | None) -> list[dict]:
    entities = {}
    def add(kind, value, provenance="User submission"):
        key = entity_id(kind, value)
        entities[key] = {"id": key, "type": kind, "value": value, "provenance": provenance}
    if claimed_org:
        add("organization", claimed_org)
    email = analyze_email_security(content)
    if email["sender_email"]:
        add("email", email["sender_email"], "Submitted email header or address; authenticity unverified")
    for url in re.findall(r"https?://[^\s<>\"']+", content):
        try:
            if urlsplit(url).hostname:
                add("domain", urlsplit(url).hostname)
        except ValueError:
            pass
    for domain in re.findall(r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|in|xyz|online|top|io)\b", content):
        add("domain", domain.lower())
    for payment in analyze_payment_risk(content)["upi_handles"]:
        add("payment", payment)
    for phone in re.findall(r"\+\d[\d -]{8,17}\d", content):
        add("phone", phone.strip())
    return list(entities.values())


def refresh_investigation(state: dict) -> dict:
    external = []
    for research in state["research"]:
        for source in research.get("sources", []):
            external.append({"id": "research-" + source["id"], "category": "external_research", "severity": "low",
                "evidence": source["title"], "source": source["url"], "confidence": 0.5,
                "explanation": "Search excerpt, not confirmation of the sender or offer.",
                "observed_value": source["extracted_information"], "timestamp": source["retrieved_at"],
                "origin": "EXTERNAL_SOURCE", "verification_status": source["verification_status"],
                "correlation_group": "external_research:" + (urlsplit(source["url"]).hostname or "unknown")})
    state["evidence"] = normalize_evidence(state["evidence"] + external)
    state["fusion"] = fuse_evidence(state["evidence"], state["coverage_checks"])
    state["graph"] = build_trust_graph(state["entities"], state["evidence"], state["research"])
    state["recommendations"] = recommend(state["entities"], state["evidence"], state["history"],
        bool(settings.TAVILY_API_KEY), settings.MAX_RESEARCH_CALLS - state["research_calls"], bool(organization_reference(state.get("claimed_organization"))))
    state["status"] = "PARTIAL" if state["fusion"]["unknowns"] else "COMPLETED"
    return state


async def investigate(content: str, baseline: dict, *, perform_research: bool = True, use_llm: bool = True) -> dict:
    evidence = normalize_evidence(baseline["evidence"])
    org = baseline.get("claimed_organization")
    entities = extract_entities(redact_sensitive_credentials(content), org)
    for finding in evidence:
        if not finding["related_entities"]:
            finding["related_entities"] = [e["id"] for e in entities if e["value"].lower() in finding["evidence"].lower()]
    org_ref = organization_reference(org)
    official = [d for d in (org_ref or {}).get("official_domains", []) if "/" not in d]
    if perform_research and org:
        query = f'{org[:100]} official careers recruitment fees'
        research = await TavilyService().search(query, official)
        calls = int(bool(settings.TAVILY_API_KEY))
    else:
        research = ResearchResult(status="SEARCH_NOT_PERFORMED", reason="No organization identified or historical snapshot")
        calls = 0
    checks = [
        {"name": "Content rules", "completed": bool(content.strip()), "reason": "No extracted text"},
        {"name": "Payment and sensitive-data rules", "completed": bool(content.strip()), "reason": "No extracted text"},
        {"name": "URL structure", "completed": any(e["type"] == "domain" for e in entities), "reason": "No submitted domain"},
        {"name": "Organization reference", "completed": bool(org_ref), "reason": "No reference match"},
        {"name": "Sender authenticity", "completed": False, "reason": "Pasted addresses and headers do not authenticate a sender"},
        {"name": "Domain registration", "completed": False, "reason": "No live RDAP adapter"},
        {"name": "Live DNS", "completed": baseline.get("dns_completed", False), "reason": "Disabled, unavailable or synthetic"},
        {"name": "TLS", "completed": baseline.get("tls_completed", False), "reason": "Disabled, unavailable or synthetic"},
        {"name": "Independent research", "completed": research.status == "COMPLETED", "reason": research.reason},
        {"name": "Specific offer authorization", "completed": False, "reason": "Requires confirmation from organization"},
    ]
    fallback = deterministic_summary(evidence)
    state = {"version": 1, "revision": 1, "entities": entities, "evidence": evidence,
        "research": [research.model_dump()], "research_calls": calls, "coverage_checks": checks,
        "history": [], "monetary_entities": baseline.get("monetary_entities", []),
        "document_extraction": baseline.get("document_extraction"), "claimed_organization": org, "official_domains": official,
        "language": await explain(content, evidence, fallback) if use_llm else {**fallback, "provider": "deterministic", "mode": "FALLBACK"},
        "baseline": {k: v for k, v in baseline.items() if k != "investigation"}}
    state["baseline"]["evidence"] = evidence
    return refresh_investigation(state)
