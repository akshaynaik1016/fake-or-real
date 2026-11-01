import re
import asyncio
from app.core.config import settings
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.scanners.url_scanner import analyze_url_security
from app.scanners.domain_scanner import analyze_domain_intelligence
from app.scanners.ssl_scanner import analyze_ssl_certificate
from app.scanners.org_scanner import verify_organization_domain_match, identify_claimed_organization
from app.scanners.email_scanner import analyze_email_security
from app.scanners.phone_scanner import analyze_phone_security
from app.scanners.text_scanner import analyze_scam_language
from app.scanners.payment_scanner import analyze_payment_risk
from app.scanners.sensitive_data_scanner import analyze_sensitive_data_requests
from app.scanners.salary_scanner import analyze_salary_anomaly
from app.scanners.similarity_scanner import analyze_job_description_similarity
from app.integrations.threat_intel.manager import threat_intel_manager
from app.services.scoring_engine import calculate_trust_and_risk
from app.services.confidence_engine import calculate_analysis_confidence
from app.security.ssrf import validate_url_safe

async def execute_full_scan(
    input_type: str,
    content: str,
    target_identifier: Optional[str] = None,
    extracted_metadata: Optional[Dict[str, Any]] = None,
    synthetic: bool = False,
    perform_research: bool = True,
    use_llm: bool = True
) -> Dict[str, Any]:
    """
    Unified multi-layer digital trust & safety analysis engine.
    Orchestrates URL, domain, SSL, organization, email, phone, text, payment,
    sensitive data, salary, and threat intelligence checks.
    """
    now = datetime.now(timezone.utc)
    evidence_list: List[Dict[str, Any]] = []
    risk_indicators: List[Dict[str, Any]] = []
    timeline: List[Dict[str, Any]] = []
    
    def log_timeline(step: str, status: str, details: str):
        timeline.append({
            "timestamp_str": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "step": step,
            "status": status,
            "details": details
        })

    log_timeline("Submission Received", "info", f"Received opportunity input via {input_type.upper()} channel.")

    # 1. Extract embedded URLs, emails, domains, phone numbers from content
    embedded_urls = re.findall(r"https?://[^\s<>\"']+", content)
    primary_url = None
    primary_domain = None
    
    if input_type == "url":
        primary_url = (extracted_metadata or {}).get("source_url") or content.strip()
    elif embedded_urls:
        primary_url = embedded_urls[0]
        
    # Check SSRF on URL if present
    if primary_url:
        is_safe_url, clean_url_or_err = validate_url_safe(primary_url, resolve_dns=False)
        if not is_safe_url:
            evidence_list.append({
                "category": "url_security",
                "severity": "critical",
                "evidence": f"URL failed SSRF validation: {clean_url_or_err}",
                "source": "SSRF Protection Layer",
                "confidence": 1.0,
                "explanation": "Target points to a restricted internal network address or cloud metadata endpoint."
            })
            log_timeline("SSRF Gate", "critical", "Blocked destination pointing to internal address space.")
            primary_url = None
        else:
            primary_url = clean_url_or_err

    # 2. URL Security Analysis
    url_analysis = None
    if primary_url:
        url_analysis = analyze_url_security(primary_url)
        primary_domain = url_analysis["registrable_domain"]
        log_timeline("URL Security Analysis", "passed" if not url_analysis["flags"] else "warning", f"Isolated registrable domain: '{primary_domain}'.")
        for flag in url_analysis["flags"]:
            evidence_list.append({
                "category": "url_security",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "URL Security Investigator",
                "observed_value": primary_url,
                "correlation_group": "identity" if flag["code"] == "BRAND_LOOKALIKE_IMPERSONATION" else "domain_infrastructure",
                "confidence": 0.95,
                "explanation": flag["detail"]
            })
            risk_indicators.append({
                "name": flag["code"],
                "description": flag["message"],
                "weight": 1.5,
                "is_positive": False
            })

    # If domain wasn't found from URL, look for domain patterns in content
    if not primary_domain:
        domain_match = re.search(r"\b([a-zA-Z0-9-]+\.(?:com|org|net|in|xyz|co|online|top|io))\b", content)
        if domain_match:
            primary_domain = domain_match.group(1).lower()

    # 3. Domain Intelligence & DNS Analysis
    domain_analysis = None
    if primary_domain:
        domain_analysis = await asyncio.to_thread(analyze_domain_intelligence, primary_domain, synthetic)
        status_tl = "warning" if domain_analysis["flags"] else "passed"
        log_timeline("Domain Intelligence", status_tl, f"Domain age: {domain_analysis['age_days']} days. MX: {'Yes' if domain_analysis['has_mx'] else 'No'}.")
        for flag in domain_analysis["flags"]:
            evidence_list.append({
                "category": "domain_intelligence",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Domain & DNS Intelligence",
                "confidence": 0.92,
                "explanation": flag["detail"]
            })
            risk_indicators.append({
                "name": flag["code"],
                "description": flag["message"],
                "weight": 1.2,
                "is_positive": False
            })
    else:
        log_timeline("Domain Intelligence", "info", "No independent domain identified for DNS lookup.")

    # 4. SSL / TLS Certificate Analysis
    ssl_analysis = None
    if primary_domain:
        ssl_analysis = await asyncio.to_thread(analyze_ssl_certificate, primary_domain, synthetic=synthetic)
        log_timeline("SSL/TLS Analysis", "passed" if ssl_analysis["is_valid"] else "warning", f"Certificate issuer: {ssl_analysis['issuer'] or 'None'}.")
        for flag in ssl_analysis["flags"]:
            evidence_list.append({
                "category": "ssl_security",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "SSL/TLS Inspector",
                "confidence": 0.90,
                "explanation": flag["detail"]
            })

    # 5. Organization Identification & Domain Matching
    claimed_org = target_identifier
    if not claimed_org:
        detected_org_info = identify_claimed_organization(content)
        if detected_org_info:
            claimed_org = detected_org_info["canonical_name"]
            
    org_verification = None
    if claimed_org and primary_domain:
        org_verification = verify_organization_domain_match(claimed_org, primary_domain)
        log_timeline("Organization Verification", "passed" if org_verification["verified"] else ("critical" if org_verification["mismatch"] else "warning"), org_verification["explanation"])
        if org_verification["mismatch"]:
            evidence_list.append({
                "category": "organization_verification",
                "severity": "critical",
                "evidence": f"Claimed organization: '{claimed_org}' does not match analyzed domain '{primary_domain}'.",
                "source": "Bundled organization domain reference",
                "confidence": 0.98,
                "explanation": org_verification["explanation"]
            })
            risk_indicators.append({
                "name": "CRITICAL_IDENTITY_MISMATCH",
                "description": org_verification["explanation"],
                "weight": 2.5,
                "is_positive": False
            })
        elif org_verification["verified"]:
            evidence_list.append({
                "category": "organization_verification",
                "severity": "verified",
                "evidence": f"Domain '{primary_domain}' verified as official infrastructure for {claimed_org}.",
                "source": "Bundled organization domain reference",
                "confidence": 0.99,
                "explanation": org_verification["explanation"]
            })
            risk_indicators.append({
                "name": "OFFICIAL_ORGANIZATION_DOMAIN_VERIFIED",
                "description": f"Domain '{primary_domain}' officially verified.",
                "weight": 2.0,
                "is_positive": True
            })

    # 6. Email Security Analysis
    email_analysis = analyze_email_security(content)
    if email_analysis["sender_email"] or email_analysis["display_name"]:
        log_timeline("Email Header Analysis", "warning" if email_analysis["flags"] else "passed", f"Sender: {email_analysis['sender_email'] or 'Unknown'}.")
        for flag in email_analysis["flags"]:
            evidence_list.append({
                "category": "email_security",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Email Header Investigator",
                "confidence": 0.95,
                "explanation": flag["detail"]
            })

    # 7. Phone Security Analysis
    phone_analysis = analyze_phone_security(content, synthetic=synthetic)
    if phone_analysis["community_reports_count"] > 0:
        log_timeline("Phone Abuse Check", "warning", f"Identified contact number with {phone_analysis['community_reports_count']} community reports.")
        for flag in phone_analysis["flags"]:
            evidence_list.append({
                "category": "phone_security",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Telecom & Community Abuse Registry",
                "confidence": 0.88,
                "explanation": flag["detail"]
            })

    # 8. External Threat Intelligence Aggregation
    threat_query_target = primary_url or (f"https://{primary_domain}" if primary_domain else None)
    threat_intel = None
    if threat_query_target:
        threat_intel = await threat_intel_manager.aggregate_threat_intelligence(threat_query_target, synthetic=synthetic)
        log_timeline("Threat Intelligence", "critical" if threat_intel["is_flagged"] else "passed", threat_intel["threat_summary"])
        if threat_intel["is_flagged"]:
            evidence_list.append({
                "category": "threat_intelligence",
                "severity": "critical",
                "evidence": f"Flagged by threat intelligence: {', '.join(threat_intel['threat_types'])}",
                "source": "External Threat Intelligence Network",
                "confidence": 0.96,
                "explanation": "Domain or URL is listed on public threat intelligence blacklists for phishing, impersonation, or advance fee fraud."
            })
            risk_indicators.append({
                "name": "THREAT_INTELLIGENCE_BLACKLISTED",
                "description": threat_intel["threat_summary"],
                "weight": 2.0,
                "is_positive": False
            })

    # 9. Scam Language & NLP Urgency Analysis
    text_scam_analysis = analyze_scam_language(content)
    if text_scam_analysis["total_indicators"] > 0:
        log_timeline("Scam Language Detection", "warning", f"Detected {text_scam_analysis['total_indicators']} linguistic risk markers.")
        for flag in text_scam_analysis["flags"]:
            evidence_list.append({
                "category": f"scam_language_{flag['category']}",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Scam Language NLP Engine",
                "confidence": 0.90,
                "explanation": flag["explanation"],
                "observed_value": flag["snippet"]
            })

    # 10. Payment Risk Analysis
    payment_risk = analyze_payment_risk(content)
    if payment_risk["payment_detected"]:
        log_timeline("Payment Risk Engine", "critical", "Upfront payment demand or fee detected.")
        for flag in payment_risk["flags"]:
            evidence_list.append({
                "category": "payment_risk",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Payment Risk Engine",
                "observed_value": flag["observed_value"],
                "source_spans": flag["source_spans"],
                "confidence": 0.97,
                "explanation": flag["detail"]
            })
            risk_indicators.append({
                "name": flag["code"],
                "description": flag["message"],
                "weight": 2.0,
                "is_positive": False
            })

    # 11. Sensitive Data Requests
    sensitive_data = analyze_sensitive_data_requests(content)
    if sensitive_data["items"]:
        sev_status = "critical" if sensitive_data["has_critical"] else "warning"
        log_timeline("Sensitive Data Audit", sev_status, f"Requested items: {', '.join([i['label'] for i in sensitive_data['items']])}.")
        for flag in sensitive_data["flags"]:
            evidence_list.append({
                "category": "sensitive_data_request",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Sensitive Data Inspector",
                "confidence": 0.94,
                "explanation": flag["detail"]
            })

    # 12. Salary & Compensation Anomaly
    salary_analysis = analyze_salary_anomaly(content)
    if salary_analysis["anomaly_detected"]:
        log_timeline("Compensation Analysis", "warning", "Compensation anomaly detected vs minimal requirements.")
        for flag in salary_analysis["flags"]:
            evidence_list.append({
                "category": "salary_anomaly",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Compensation Anomaly Model",
                "confidence": 0.85,
                "explanation": flag["detail"]
            })

    # 13. Job Description Semantic Similarity
    similarity_analysis = analyze_job_description_similarity(content)
    if similarity_analysis["matched"]:
        log_timeline("Similarity Engine", "warning", f"Template overlap: {similarity_analysis['similarity_percentage']}%.")
        for flag in similarity_analysis["flags"]:
            evidence_list.append({
                "category": "template_similarity",
                "severity": flag["severity"],
                "evidence": flag["message"],
                "source": "Semantic Similarity Corpus",
                "confidence": 0.88,
                "explanation": flag["detail"]
            })

    # 14. Document Inconsistencies (from PDF or OCR metadata if provided)
    if extracted_metadata and extracted_metadata.get("flags"):
        for flag in extracted_metadata["flags"]:
            evidence_list.append({
                "category": "document_integrity",
                "severity": flag.get("severity", "moderate"),
                "evidence": flag.get("message", "Document manipulation indicators detected"),
                "source": "Document Integrity Analyzer",
                "confidence": 0.85,
                "explanation": flag.get("detail", "Metadata inconsistencies observed.")
            })

    # Retain original observed values alongside rule interpretations.
    for ev in evidence_list:
        if "observed_value" not in ev:
            cat = ev["category"]
            if cat == "payment_risk":
                ev["observed_value"] = "; ".join(payment_risk.get("purposes_found", []) + payment_risk.get("upi_handles", []) + [a["raw"] for a in payment_risk.get("payment_amounts", [])])
            elif cat == "sensitive_data_request":
                ev["observed_value"] = "; ".join(i["match"] for i in sensitive_data["items"])
            elif cat == "organization_verification":
                ev["observed_value"] = f"{claimed_org} | {primary_domain}"
                ev["verification_status"] = "BUNDLED_REFERENCE_COMPARISON"
            elif cat == "email_security":
                ev["observed_value"] = email_analysis["from_header"]
            elif cat in {"domain_intelligence", "ssl_security"}:
                ev["observed_value"] = primary_domain or "No domain observed"
            elif cat == "phone_security":
                ev["observed_value"] = phone_analysis["phone_number"]
            elif cat == "salary_anomaly":
                ev["observed_value"] = salary_analysis.get("claimed_amount") or "Not extracted"
            elif cat == "template_similarity":
                ev["observed_value"] = f"TF-IDF similarity {similarity_analysis.get('similarity_percentage')}%"
            elif cat == "document_integrity":
                ev["observed_value"] = str((extracted_metadata or {}).get("metadata", {}))[:1000]

    # Preserve fixture provenance; it must never contribute to real-world fusion.
    for ev in evidence_list:
        fixture = (ev["category"] == "domain_intelligence" and domain_analysis and domain_analysis.get("is_demo_source")) or (
            ev["category"] == "ssl_security" and ssl_analysis and ssl_analysis.get("is_demo_source")) or (
            ev["category"] == "phone_security" and synthetic) or (
            ev["category"] == "threat_intelligence" and threat_intel and not threat_intel.get("live_flagged"))
        if fixture:
            ev.update(origin="SYNTHETIC", verification_status="SYNTHETIC")
            ev["source"] = "Synthetic fixture: " + ev["source"]
        elif ev["category"] == "ssl_security" and ssl_analysis.get("status") == "UNAVAILABLE":
            ev.update(verification_status="UNAVAILABLE")

    # 15. Compute Final Trust Score & Risk Level
    trust_score, risk_level, breakdown = calculate_trust_and_risk(evidence_list)
    confidence_score = calculate_analysis_confidence(evidence_list, len(timeline), len(content))
    log_timeline("Risk Assessment Finalized", "passed" if risk_level == "LOW RISK" else "critical", f"Trust Score: {trust_score}/100 ({risk_level}). Confidence: {confidence_score}%.")

    # Checklist execution states are independent of risk severity and coverage.
    from app.services.verification_service import build_verification_checklist
    verification_checks = build_verification_checklist(
        content=content, domain=primary_domain, org=claimed_org, organization=org_verification,
        dns=domain_analysis, tls=ssl_analysis, email=email_analysis, phone=phone_analysis,
        threat=threat_intel, payment=payment_risk, sensitive=sensitive_data,
        document=extracted_metadata, synthetic=synthetic)
    if synthetic:
        for event in timeline:
            if event["step"] in {"Domain Intelligence", "SSL/TLS Analysis", "Threat Intelligence"}:
                event["details"] = "[Synthetic fixture] " + event["details"]

    # 17. Context-Aware Safety Recommendations
    recommendations = []
    if payment_risk["payment_detected"]:
        recommendations.append("Do not pay the requested registration fee or security deposit. Legitimate employers and internships do not charge fees to candidates.")
    if sensitive_data["has_critical"]:
        recommendations.append("NEVER share OTP, UPI PIN, ATM PIN, passwords, or CVV. Legitimate organizations never request authentication codes.")
    if sensitive_data["has_medium"]:
        recommendations.append("Do not upload Aadhaar, PAN card, or bank passbook until you have independently confirmed the company's identity via official channels.")
    if org_verification and org_verification["mismatch"]:
        recommendations.append(f"Visit {org_verification['canonical_name']}'s official careers portal ({org_verification.get('official_careers_url', 'official website')}) directly to verify if this opportunity exists.")
    if email_analysis["is_free_webmail"]:
        recommendations.append("Verify recruiter identity through official corporate channels. Free personal email accounts (Gmail, Yahoo) are not used for official corporate hiring.")
    if primary_domain and domain_analysis and (domain_analysis["age_days"] is not None and domain_analysis["age_days"] < 30):
        recommendations.append("The domain was registered recently. Avoid entering personal credentials or downloading files from this domain.")
        
    recommendations.append("Preserve screenshots, transaction records, and communication logs in case of future verification or reporting.")
    recommendations.append("Contact the organization directly using phone numbers and emails found independently on their verified website.")

    summary = (
        f"Legacy deterministic baseline: Trust Score {trust_score}/100 ({risk_level}); legacy confidence index {confidence_score}/100 (uncalibrated). "
        f"{len(evidence_list)} findings recorded. Consult Evidence Fusion for investigation coverage and unknowns."
    )

    result = {
        "status": "COMPLETED",
        "trust_score": trust_score,
        "risk_level": risk_level,
        "analysis_confidence": confidence_score,
        "summary": summary,
        "evidence": evidence_list,
        "indicators": risk_indicators,
        "verification_results": verification_checks,
        "recommended_actions": recommendations,
        "timeline": timeline,
        "threat_intel_details": threat_intel,
        "claimed_organization": claimed_org,
        "primary_domain": primary_domain,
        "monetary_entities": payment_risk["monetary_entities"],
        "document_extraction": extracted_metadata if input_type in {"screenshot", "pdf"} else None
    }

    result["dns_completed"] = bool(domain_analysis and domain_analysis.get("status") == "COMPLETED")
    result["tls_completed"] = bool(ssl_analysis and ssl_analysis.get("is_valid") and not ssl_analysis.get("is_demo_source"))
    from app.agents.investigation_orchestrator import investigate
    result["investigation"] = await investigate(content, result, perform_research=perform_research, use_llm=use_llm)
    return result
