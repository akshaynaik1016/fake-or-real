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
        for pattern_regex, label in patterns:
            matches = re.finditer(pattern_regex, text)
            for match in matches:
                matched_snippet = match.group(0)
                if category == "payment_pressure":
                    from app.scanners.payment_scanner import negated_payment_context
                    if negated_payment_context(text, match.start()):
                        continue
                detected_categories.add(category)
                
                # Determine severity
                if category == "credential_harvesting":
                    sev = "critical"
                elif category == "payment_pressure":
                    sev = "critical"
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
                    "message": f"{label}: '{matched_snippet}' detected in submission.",
                    "explanation": f"Fraudulent opportunities heavily utilize {category.replace('_', ' ')} to induce hasty decisions before independent verification."
                })
                
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
