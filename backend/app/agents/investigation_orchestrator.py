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
                "source_id":source["id"],"original_excerpt":source["extracted_information"],"extracted_value":source["extracted_information"],"extraction_method":"tavily_search","claim_type":"external_context","provenance_kind":"INDEPENDENTLY_RETRIEVED_CONTEXT",
                "correlation_group": "external_research:" + (urlsplit(source["url"]).hostname or "unknown")})
    from app.services.notice_verification import compare_notice,notice_evidence,notice_action
    state['notice_review']=compare_notice(state.get('claims',[]),state['research'])
    retained=[e for e in state['evidence'] if e['category'] not in {'notice_corroboration','notice_contradiction','notice_possible_inconsistency','recruitment_policy_conflict'}]
    from app.services.recruitment_consistency import internal_policy_findings
    state["evidence"] = normalize_evidence(retained + external + notice_evidence(state['notice_review'])+internal_policy_findings(state.get('claims',[])))
    for finding in state['evidence']:
        if not finding.get('source_id'):finding['source_id']=state.get('source_id')
        if finding.get('extracted_value') is None:finding['extracted_value']=finding['observed_value']
        if not finding.get('claim_type'):finding['claim_type']=finding['category']
        matching=next((c for c in state.get('claims',[]) if c['excerpt']==finding['observed_value']),None)
        if matching and not finding.get('original_excerpt'):
            finding['original_excerpt']=matching['excerpt'];finding['source_spans']=[{**matching['location'],'text':matching['excerpt'],'kind':matching['claim_type']}]
            finding['provenance_kind']='OBSERVED_IN_SUBMISSION'
    state["fusion"] = fuse_evidence(state["evidence"], state["coverage_checks"])
    state["graph"] = build_trust_graph(state["entities"], state["evidence"], state["research"])
    state["recommendations"] = recommend(state["entities"], state["evidence"], state["history"],
        bool(settings.TAVILY_API_KEY), settings.MAX_RESEARCH_CALLS - state["research_calls"], bool(organization_reference(state.get("claimed_organization"))))
    action=notice_action(state.get('claims',[]),state['research_calls'],state['history'],state['research'])
    if action:state['recommendations'].insert(0,action)
    from app.services.recruitment_graph import enrich_recruitment_graph
    state['graph']=enrich_recruitment_graph(state['graph'],state.get('claims',[]),state['notice_review'],'submission')
    state["status"] = "PARTIAL" if state["fusion"]["unknowns"] else "COMPLETED"
    from app.services.assessment_semantics import integrity_view
    return integrity_view(state)


async def investigate(content: str, baseline: dict, *, perform_research: bool = True, use_llm: bool = True) -> dict:
    evidence = normalize_evidence(baseline["evidence"])
    org = baseline.get("claimed_organization")
    entities = extract_entities(redact_sensitive_credentials(content), org)
    for finding in evidence:
        if not finding["related_entities"]:
            finding["related_entities"] = [e["id"] for e in entities if e["value"].lower() in finding["evidence"].lower()]
    from app.services.case_claims import extract_claims
    import hashlib
    source_id='submission-'+hashlib.sha256(content.encode()).hexdigest()[:20]
    claims=extract_claims(source_id,content,baseline.get('input_type','text'))
    org_ref = organization_reference(org)
    official = [d for d in (org_ref or {}).get("official_domains", []) if "/" not in d]
    if perform_research and org:
        from app.services.notice_verification import anchors
        exact=anchors(claims)
        query = (f'"{exact["advertisement_number"]}" {org[:100]} {exact["job_title"]}' if exact else f'{org[:100]} official careers recruitment fees')[:250]
        research = await TavilyService().search(query, official)
        calls = int(bool(settings.TAVILY_API_KEY))
    else:
        research = ResearchResult(status="SEARCH_NOT_PERFORMED", reason="Research was not requested for this source; no external verification was performed." if org else "No organization claim identified; external research was not performed.")
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
    # Ground rule findings in exact submitted spans whenever retained by the scanner.
    for finding in evidence:
        finding['source_id']=source_id
        finding['claim_type']=finding['category']
        finding['extracted_value']=finding['observed_value']
        finding['extraction_method']='deterministic_rule' if finding['origin']=='DETERMINISTIC_RULE' else finding['origin'].lower()
        spans=finding.get('source_spans',[])
        if not spans and finding['observed_value'] in content and finding['observed_value']:
            start=content.index(finding['observed_value'])
            spans=[{'start':start,'end':start+len(finding['observed_value']),'text':finding['observed_value'],'kind':'observation'}]
            finding['source_spans']=spans
        finding['original_excerpt']=spans[0]['text'] if spans else None
        finding['provenance_kind']='OBSERVED_IN_SUBMISSION' if spans else 'RULE_OUTPUT'
    fallback = deterministic_summary(evidence)
    state = {"version": 2, "revision": 1,"source_id":source_id,"claims":claims, "entities": entities, "evidence": evidence,
        "research": [research.model_dump()], "research_calls": calls, "coverage_checks": checks,
        "history": [], "monetary_entities": baseline.get("monetary_entities", []),
        "document_extraction": baseline.get("document_extraction"), "claimed_organization": org, "official_domains": official,
        "language": await explain(content, evidence, fallback) if use_llm else {**fallback, "provider": "deterministic", "mode": "FALLBACK"},
        "baseline": {k: v for k, v in baseline.items() if k != "investigation"}}
    state["baseline"]["evidence"] = evidence
    return refresh_investigation(state)
