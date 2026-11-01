"""Normalize retained scanner findings without manufacturing observations."""
from datetime import datetime, timezone
from uuid import uuid5, NAMESPACE_URL
from app.schemas.investigation import Evidence
from app.security.redaction import redact_sensitive_credentials


def evidence_group(category: str) -> str:
    if "payment" in category or "fee" in category:
        return "payment"
    if "credential" in category:
        return "sensitive_data"
    if any(k in category for k in ("domain", "dns", "ssl", "url")):
        return "domain_infrastructure"
    if any(k in category for k in ("organization", "email", "identity_match")):
        return "identity"
    if "payment" in category:
        return "payment"
    if any(k in category for k in ("sensitive", "credential")):
        return "sensitive_data"
    if any(k in category for k in ("language", "content", "salary", "similarity")):
        return "content_patterns"
    return category


def group_evidence(rows: list[dict],across_sources=False) -> list[dict]:
    """Rule-normalized semantic facts; multiple exact references, one conclusion.

    Unspecified/general language is never merged by fuzzy text similarity. Distinct
    recipient/channel/amount contexts are encoded in payment fact keys.
    """
    from copy import deepcopy
    grouped={};rank={'critical':5,'high':4,'moderate':3,'low':2,'verified':1}
    for original in rows:
        row=deepcopy(original);fact=row.get('fact_key')
        key=(None if across_sources else row.get('source_id'),row.get('origin','DETERMINISTIC_RULE'),fact) if fact else ('id',row.get('id') or str(uuid5(NAMESPACE_URL,str((row.get('category'),row.get('source'),row.get('evidence'))))))
        if key not in grouped:grouped[key]=row;continue
        current=grouped[key]
        citations=[*current.get('citations',[]),*row.get('citations',[])]
        current['citations']=list({(c.get('source_id'),c.get('field'),c.get('start'),c.get('end'),c.get('excerpt')):c for c in citations}.values())
        if current.get('source_id')==row.get('source_id'):
            current['source_spans']=list({(s.get('start'),s.get('end'),s.get('kind')):s for s in [*current.get('source_spans',[]),*row.get('source_spans',[])]}.values())
        current['source_ids']=list(dict.fromkeys([*current.get('source_ids',[]),*row.get('source_ids',[]),*[r['source_id'] for r in (current,row) if r.get('source_id')]]))
        contexts={(c.get('source_id'),c.get('start'),c.get('end')) for c in current['citations'] if c.get('field')=='extracted_text'}
        current['occurrences']=max(current.get('occurrences',1),row.get('occurrences',1),len(contexts))
        if rank.get(row.get('severity'),0)>rank.get(current.get('severity'),0):
            for k in ['severity','evidence','explanation','confidence']:current[k]=row.get(k,current.get(k))
    return list(grouped.values())


def normalize_evidence(rows: list[dict]) -> list[dict]:
    output = []
    seen = set()
    for row in group_evidence(rows):
        row = dict(row)
        category = row["category"]
        value = redact_sensitive_credentials(row["evidence"])
        if row.get("origin") == "SYNTHETIC" and not value.startswith("[Synthetic fixture]"):
            value = "[Synthetic fixture] " + value
        evidence_id = row.get("id") or str(uuid5(NAMESPACE_URL, f"{category}:{row['source']}:{value}"))
        if evidence_id in seen:
            continue
        seen.add(evidence_id)
        output.append(Evidence(
            id=evidence_id, category=category, severity=row["severity"], evidence=value,
            source=row["source"], confidence=row.get("confidence", 0.5),
            explanation=redact_sensitive_credentials(row.get("explanation") or ""),
            timestamp=row.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            # Legacy scanner messages are interpretations, not captured raw matches.
            observed_value=redact_sensitive_credentials(row.get("observed_value", "Raw match not retained by legacy scanner")),
            origin=row.get("origin", "DETERMINISTIC_RULE"),
            verification_status=row.get("verification_status", "NOT_INDEPENDENTLY_VERIFIED"),
            correlation_group=row.get("correlation_group", evidence_group(category)),
            related_entities=row.get("related_entities", []),
            source_spans=row.get("source_spans", []),
            **{key:row[key] for key in ['source_id','original_excerpt','extracted_value','extraction_method','claim_type','provenance_kind','verified_claim_id','verification_scope','fact_key','occurrences','payment_context','citations','source_ids'] if key in row}).model_dump())
    return output


def deterministic_summary(evidence: list[dict], limit: int = 5) -> dict:
    rank = {"critical": 0, "high": 1, "moderate": 2, "low": 3, "verified": 4}
    observed = sorted((e for e in evidence if e["origin"] not in {"SYNTHETIC", "EXTERNAL_SOURCE"}),
                      key=lambda e: rank.get(e["severity"], 5))
    return {"interpretations": [{"text": e["evidence"] + " " + e["explanation"],
                                 "evidence_ids": [e["id"]]} for e in observed[:limit]], "claims": []}
