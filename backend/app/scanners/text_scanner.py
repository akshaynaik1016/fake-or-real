import re
from typing import Dict, Any, List

SCAM_PATTERNS = {
    "payment_pressure": [
        (r"(?i)\b(registration|security|training|processing|certificate|verification|laptop|courier)\s+(fee|deposit|charges?|amount)\b", "Upfront fee/deposit requirement"),
        (r"(?i)\b(refundable|mandatory)\s+(deposit|fee|payment)\b", "Refundable/mandatory deposit claim"),
        (r"(?i)\bpay\s+(rs\.?|inr|₹|\$)\s*[\d,]+", "Explicit payment demand"),
        (r"(?i)\bpay\s+before\s+(interview|joining|offer|test)\b", "Payment required before joining or interview"),
    ],
    "urgency": [
        (r"(?i)\b(act\s+immediately|offer\s+expires\s+today|within\s+\d+\s+(hours|minutes)|pay\s+within\s+\d+\s+mins?)\b", "Artificial urgency time limit"),
        (r"(?i)\b(only\s+\d+\s+seats?\s+left|last\s+chance|immediate\s+confirmation\s+required)\b", "Scarcity / seat pressure"),
        (r"(?i)\blimited\s+(seats?|slots?|openings?)\s+available\b", "High scarcity claim")
    ],
    "credential_harvesting": [
        (r"(?i)\b(send|share|provide|enter)\s+(your\s+)?(otp|upi\s+pin|atm\s+pin|cvv|password|netbanking\s+password)\b", "Critical credential request (OTP/PIN/Password)"),
        (r"(?i)\b(submit|upload)\s+(aadhaar|pan\s+card|bank\s+passbook|cheque)\s+(immediately|now)\b", "Sensitive identity/financial document harvesting"),
    ],
    "emotional_manipulation": [
        (r"(?i)\b(congratulations|congrats)!?\s+you\s+(have\s+been|are)\s+(selected|shortlisted|chosen)\b", "Unsolicited selection / congratulatory bait"),
        (r"(?i)\b(specially\s+selected|exclusive\s+invitation|secret\s+opportunity)\b", "Exclusivity manipulation"),
        (r"(?i)\b(guaranteed\s+(income|placement|job|salary)|100%\s+selection)\b", "Guaranteed outcome promise"),
        (r"(?i)\b(earn\s+(from\s+home|online)|part-time\s+work\s+daily)\b", "Work-from-home earn quick money hook")
    ]
}

def analyze_scam_language(text: str) -> Dict[str, Any]:
    """
    Performs deterministic pattern matching and NLP heuristics across scam taxonomy:
    - Payment pressure
    - Urgency
    - Credential harvesting
    - Emotional manipulation
    """
    if not text:
        return {"categories_detected": [], "flags": [], "total_indicators": 0}
        
    detected_categories = set()
    flags = []
    
    for category, patterns in SCAM_PATTERNS.items():
        # These subjects are delegated to their contextual scanners. The unified
        # pipeline consumes those findings once, with all supporting references.
        if category in {'payment_pressure','credential_harvesting'}:continue
        for pattern_regex, label in patterns:
            matches = re.finditer(pattern_regex, text)
            for match in matches:
                matched_snippet = match.group(0)
                if label=='Guaranteed outcome promise' and re.match(r'\s+assistance\b',text[match.end():],re.I):continue
                if category == "payment_pressure":
                    from app.scanners.payment_scanner import negated_payment_context,uncertain_payment_context
                    if negated_payment_context(text, match.start()) or re.match(r"\s*(?:of|is|are|:)?\s*(?:waived|not required|none|zero|₹\s*0\b|(?:Rs\.?|INR)\s*0\b)",text[match.end():],re.I):
                        continue
                prefix=re.split(r'[.!?;\n]|\b(?:but|however)\b',text[max(0,match.start()-120):match.start()],flags=re.I)[-1]
                if re.search(r"\b(?:never|don't|do not|not required|no need to|without)\b",prefix,re.I):continue
                detected_categories.add(category)
                
                # Determine severity
                if category == "credential_harvesting":
                    sev = "critical"
                elif category == "payment_pressure":
                    sev = "moderate" if uncertain_payment_context(text,match.start()) else "critical"
                elif category == "urgency":
                    sev = "high"
                else:
                    sev = "moderate"
                    
                flags.append({
                    "category": category,
                    "severity": sev,
                    "code": f"SCAM_LANG_{category.upper()}",
                    "indicator": label,
                    "snippet": matched_snippet,
                    "source_spans":[{"start":match.start(),"end":match.end(),"text":matched_snippet,"kind":category}],
                    "message": f"{label}: '{matched_snippet}' detected in submission.",
                    "explanation": f"Fraudulent opportunities heavily utilize {category.replace('_', ' ')} to induce hasty decisions before independent verification."
                })
                
    from app.scanners.payment_scanner import analyze_payment_risk
    from app.scanners.sensitive_data_scanner import analyze_sensitive_data_requests
    for category,source_flags in [('payment_pressure',analyze_payment_risk(text)['flags']),('credential_harvesting',[f for f in analyze_sensitive_data_requests(text)['flags'] if f['severity']=='critical'])]:
        for f in source_flags:
            detected_categories.add(category)
            flags.append({'category':category,'severity':f['severity'],'code':f['code'],'indicator':f['code'],
                'snippet':f['observed_value'],'source_spans':f['source_spans'],'message':f['message'],'explanation':f['detail']})
    cats = list(detected_categories)
    urgency_detected = "urgency" in detected_categories
    manipulation_detected = "emotional_manipulation" in detected_categories

    return {
        "categories_detected": cats,
        "matched_categories": cats,
        "flags": flags,
        "total_indicators": len(flags),
        "has_credential_harvesting": "credential_harvesting" in detected_categories,
        "has_payment_pressure": "payment_pressure" in detected_categories,
        "has_urgency": urgency_detected,
        "urgency_detected": urgency_detected,
        "manipulation_detected": manipulation_detected
    }

def scan_text_patterns(text: str) -> Dict[str, Any]:
    """Test alias for analyze_scam_language."""
    return analyze_scam_language(text)
