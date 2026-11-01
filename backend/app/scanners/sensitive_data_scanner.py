import re
from typing import Dict, Any, List

SENSITIVE_DATA_TAXONOMY = {
    "CRITICAL": [
        (r"(?i)\b(otp|one\s*time\s*password)\b", "OTP (One-Time Password)"),
        (r"(?i)\b(upi\s*pin|atm\s*pin|mpin)\b", "UPI / ATM Security PIN"),
        (r"(?i)\b(cvv|cvc|security\s*code)\b", "Card CVV / Security Code"),
        (r"(?i)\b(login\s*password|netbanking\s*password|credentials)\b", "Account Password / Credentials"),
        (r"(?i)\b(card\s*number|debit\s*card\s*details|credit\s*card\s*number)\b", "Full Card Number"),
        (r"(?i)\b(biometric|fingerprint|face\s*scan\s*credentials)\b", "Biometric Authentication Data")
    ],
    "MEDIUM": [
        (r"(?i)\b(aadhaar(\s*card)?|uidai)\b", "Aadhaar Card / Number"),
        (r"(?i)\b(pan(\s*card)?|permanent\s*account\s*number)\b", "PAN Card"),
        (r"(?i)\b(passport(\s*copy|\s*number)?)\b", "Passport Details"),
        (r"(?i)\b(driving\s*licen[sc]e|voter\s*id)\b", "Driver's License / Voter ID"),
        (r"(?i)\b(bank\s*account(\s*number)?|ifsc(\s*code)?|cancelled\s*cheque)\b", "Bank Account / IFSC Details")
    ],
    "LOW": [
        (r"(?i)\b(resume|cv|curriculum\s*vitae)\b", "Resume / Curriculum Vitae"),
        (r"(?i)\b(portfolio|github\s*profile|linkedin\s*profile)\b", "Professional Portfolio / Profile"),
        (r"(?i)\b(marksheet|degree\s*certificate|college\s*id)\b", "Educational Marksheet / College ID")
    ]
}

def analyze_sensitive_data_requests(text: str) -> Dict[str, Any]:
    """
    Detects requests for sensitive data and classifies them into:
    - CRITICAL (OTP, PIN, Password, CVV)
    - MEDIUM (Aadhaar, PAN, Passport, Bank Account)
    - LOW (Resume, Portfolio, College ID)
    """
    if not text:
        return {"detected_tiers": [], "items": [], "flags": []}
        
    detected_tiers = set()
    detected_items = []
    flags = []
    
    for tier, patterns in SENSITIVE_DATA_TAXONOMY.items():
        for pattern_regex, label in patterns:
            match = re.search(pattern_regex, text)
            if match:
                detected_tiers.add(tier)
                detected_items.append({"tier": tier, "label": label, "match": match.group(0)})
                
                if tier == "CRITICAL":
                    flags.append({
                        "tier": "CRITICAL",
                        "severity": "critical",
                        "code": "CRITICAL_CREDENTIAL_REQUEST",
                        "message": f"CRITICAL: Request for {label} detected.",
                        "detail": f"Never share {label} with any recruiter, organization, or third-party portal. Legitimate employers never require OTPs, UPI PINs, passwords, or CVVs."
                    })
                elif tier == "MEDIUM":
                    flags.append({
                        "tier": "MEDIUM",
                        "severity": "moderate",
                        "code": "GOVERNMENT_ID_REQUEST",
                        "message": f"MEDIUM RISK: Request for {label} detected.",
                        "detail": f"Do not upload {label} until the organization's legitimacy and formal offer have been independently verified through official enterprise channels."
                    })
                else: # LOW
                    flags.append({
                        "tier": "LOW",
                        "severity": "low",
                        "code": "STANDARD_APPLICATION_DATA",
                        "message": f"STANDARD: Request for {label} detected.",
                        "detail": f"Requesting {label} is standard practice for recruitment and internship applications."
                    })

    has_requests = bool(detected_items)
    detected_requests = []
    for item in detected_items:
        detected_requests.append({
            "severity": item["tier"],
            "tier": item["tier"],
            "label": item["label"],
            "match": item["match"]
        })

    return {
        "detected_tiers": list(detected_tiers),
        "items": detected_items,
        "flags": flags,
        "has_critical": "CRITICAL" in detected_tiers,
        "has_medium": "MEDIUM" in detected_tiers,
        "has_sensitive_requests": has_requests,
        "detected_requests": detected_requests
    }

def scan_sensitive_data(text: str) -> Dict[str, Any]:
    """Test alias for analyze_sensitive_data_requests."""
    return analyze_sensitive_data_requests(text)
