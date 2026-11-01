import re
from typing import Dict, Any, List

# Known reported numbers in community intelligence database (demo seed)
KNOWN_REPORTED_NUMBERS = {
    "+919876543210": {
        "carrier": "Virtual VoIP / Cloud Telephony",
        "is_voip": True,
        "country": "India (+91)",
        "community_reports_count": 17,
        "sample_complaints": [
            "Requested ₹1,499 registration fee via WhatsApp for fake data entry job",
            "Impersonated Microsoft HR recruiter",
            "Sent suspicious APK download link"
        ]
    },
    "+919988776655": {
        "carrier": "Virtual / Temporary SIP",
        "is_voip": True,
        "country": "India (+91)",
        "community_reports_count": 24,
        "sample_complaints": [
            "Part-time Telegram task scam requesting UPI deposit",
            "Crypto investment competition scam"
        ]
    },
    "+12025550199": {
        "carrier": "Bandwidth.com / Google Voice VoIP",
        "is_voip": True,
        "country": "United States (+1)",
        "community_reports_count": 8,
        "sample_complaints": [
            "Fake remote scholarship processing fee request"
        ]
    }
}

def analyze_phone_security(raw_phone: str, synthetic: bool = False) -> Dict[str, Any]:
    """
    Analyzes phone number for formatting, VoIP carrier indicators,
    and associated community reports without making unverified legal assertions.
    """
    # Clean non-digit except leading +
    cleaned = re.sub(r"[^\d+]", "", raw_phone.strip())
    if not cleaned.startswith("+") and len(cleaned) == 10:
        cleaned = "+91" + cleaned # Default to India country code if 10 digits
        
    flags = []
    
    # Check known reported database
    known = KNOWN_REPORTED_NUMBERS.get(cleaned) if synthetic else None
    if known:
        report_count = known["community_reports_count"]
        flags.append({
            "code": "COMMUNITY_ABUSE_REPORTS",
            "severity": "critical" if report_count > 10 else "high",
            "message": f"Multiple community reports ({report_count}) mention payment requests and impersonation associated with this number.",
            "detail": "Community-generated information indicates repeated scam complaints. Independently verify the contact before proceeding."
        })
        if known["is_voip"]:
            flags.append({
                "code": "VOIP_VIRTUAL_NUMBER",
                "severity": "moderate",
                "message": "Phone number is routed through a virtual VoIP / cloud telephony gateway.",
                "detail": "VoIP numbers can be generated internationally with minimal KYC verification."
            })
            
        return {
            "phone_number": cleaned,
            "country": known["country"],
            "carrier": known["carrier"],
            "is_voip": known["is_voip"],
            "community_reports_count": report_count,
            "sample_complaints": known["sample_complaints"],
            "flags": flags
        }
        
    # Standard heuristic format analysis
    is_valid_format = bool(re.match(r"^\+[1-9]\d{6,14}$", cleaned))
    country = "International / E.164"
    if cleaned.startswith("+91"):
        country = "India (+91)"
    elif cleaned.startswith("+1"):
        country = "United States / Canada (+1)"
    elif cleaned.startswith("+44"):
        country = "United Kingdom (+44)"
        
    return {
        "phone_number": cleaned,
        "country": country,
        "carrier": "Standard Mobile Carrier / Fixed Line",
        "is_voip": False,
        "community_reports_count": 0,
        "sample_complaints": [],
        "flags": flags
    }
