from typing import Dict, Any, List
from app.security.redaction import redact_sensitive_credentials
from app.security.prompt_injection import format_untrusted_context_for_ai

def answer_investigator_query(
    question: str,
    scan_detail: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Answers user queries about a specific scan grounded exclusively
    in the recorded evidence, verification results, and cybersecurity risk posture.
    """
    q_clean = question.lower().strip()
    evidence_list = scan_detail.get("evidence", [])
    checks = scan_detail.get("verification_results", [])
    trust_score = scan_detail.get("trust_score")
    risk_level = scan_detail.get("risk_level", "UNDETERMINED")
    claimed_org = scan_detail.get("claimed_organization", "the claimed organization")
    primary_domain = scan_detail.get("primary_domain", "the submitted domain")
    
    referenced_evidence = []
    
    # 1. "Why is this suspicious?" / "Why is it risky?"
    if any(k in q_clean for k in ["why", "suspicious", "risky", "danger", "red flag"]):
        critical_evs = [e for e in evidence_list if e.get("severity") in ["critical", "high"]]
        if not critical_evs:
            answer = f"Assessment: {risk_level}. No critical red flags were observed; independent offer verification remains unresolved. Absence of concerns does not establish safety."
        else:
            bullets = []
            for ev in critical_evs[:3]:
                bullets.append(f"• {ev.get('evidence')}: {ev.get('explanation')}")
                referenced_evidence.append(ev.get("evidence"))
            answer = (
                f"This opportunity is flagged as **{risk_level}** due to several key forensic indicators:\n\n"
                + "\n\n".join(bullets) +
                "\n\nThese observed concerns warrant investigation; they do not independently prove fraud."
            )
        confidence_note = "Grounded directly in observed scan evidence."

    # 2. "Is this company genuine?" / "Is Microsoft real?"
    elif any(k in q_clean for k in ["company", "genuine", "real", "legit", "organization", "firm"]):
        org_ev = [e for e in evidence_list if "organization" in e.get("category", "") or "identity" in e.get("category", "")]
        if org_ev:
            top_ev = org_ev[0]
            referenced_evidence.append(top_ev.get("evidence"))
            answer = f"Organization reference finding: {top_ev.get('evidence')}. {top_ev.get('explanation')}. A reference-domain match does not authenticate a sender or a specific offer."
        else:
            answer = f"The claimed organization '{claimed_org}' could not be matched against verified corporate domain infrastructure. Independent verification via official career portals is recommended."
        confidence_note = "Based on the bundled domain reference; no live registry verification."

    # 3. "Why is the domain risky?"
    elif any(k in q_clean for k in ["domain", "url", "website"]):
        domain_ev = [e for e in evidence_list if "domain" in e.get("category", "") or "url" in e.get("category", "")]
        if domain_ev:
            bullets = [f"• {e.get('evidence')}" for e in domain_ev[:3]]
            referenced_evidence.extend([e.get("evidence") for e in domain_ev[:3]])
            answer = (
                f"The domain '{primary_domain}' shows specific forensic risks:\n"
                + "\n".join(bullets) +
                "\n\nAttackers regularly register low-cost disposable domains shortly before launching recruitment or scholarship campaigns."
            )
        else:
            answer = f"The domain '{primary_domain}' has no recorded domain risk findings in this snapshot. Missing or unavailable checks are not proof of safety."
        confidence_note = "Derived only from recorded domain findings; inspect provenance for availability."

    # 4. "What information should I avoid sharing?" / "What should I not share?"
    elif any(k in q_clean for k in ["avoid", "share", "aadhaar", "pan", "otp", "password", "bank", "sensitive"]):
        sens_ev = [e for e in evidence_list if "sensitive" in e.get("category", "") or "payment" in e.get("category", "")]
        referenced_evidence.extend([e.get("evidence") for e in sens_ev])
        answer = (
            "**Never share the following information:**\n"
            "1. **Never share OTPs, UPI PINs, ATM PINs, or Passwords** under any circumstances.\n"
            "2. **Do not pay upfront registration fees, security deposits, or laptop courier charges.**\n"
            "3. **Do not upload Aadhaar, PAN card, or bank passbook copies** until you have independently verified the recruiter's identity through official corporate channels."
        )
        confidence_note = "Based on digital trust and safety standards."

    # 5. "Can I apply?" / "What should I verify?"
    elif any(k in q_clean for k in ["apply", "what should i", "next step", "verify", "can i"]):
        actions = scan_detail.get("recommended_actions", [])
        bullets = [f"• {a}" for a in actions[:4]]
        answer = (
            f"Given the **{risk_level}** assessment, here are the recommended safe actions before taking any further steps:\n\n"
            + "\n".join(bullets)
        )
        confidence_note = "Actionable safety recommendations generated from detected risk vectors."

    # 6. "Which finding is the most serious?"
    elif any(k in q_clean for k in ["serious", "worst", "severe", "most"]):
        critical_evs = [e for e in evidence_list if e.get("severity") == "critical"]
        if critical_evs:
            top = critical_evs[0]
            referenced_evidence.append(top.get("evidence"))
            answer = (
                f"The most critical finding is: **{top.get('evidence')}**.\n\n"
                f"**Why it matters:** {top.get('explanation')}"
            )
        else:
            answer = "No critical-level findings were recorded for this opportunity."
        confidence_note = "Highest severity forensic signal prioritized."

    # 7. Fallback / Insufficient evidence
    else:
        answer = (
            f"Based on the evidence collected for this opportunity ({risk_level}; offer verification unresolved): "
            f"Consult the recorded findings and unavailable checks for this submission. "
            f"If you need specific details, ask me 'Why is this suspicious?', 'Is the company genuine?', or 'What should I verify?'"
        )
        confidence_note = "General inquiry synthesized from scan profile."

    return {
        "answer": answer,
        "grounded_in_evidence": True,
        "evidence_referenced": referenced_evidence,
        "confidence_note": confidence_note
    }
