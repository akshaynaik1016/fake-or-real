import re

def redact_sensitive_credentials(text: str) -> str:
    """
    Redacts highly sensitive personal credentials like OTPs, CVVs, passwords,
    and PINs before logging or AI processing.
    """
    if not text:
        return ""
        
    redacted = text
    
    # Redact CVV (3 or 4 digits preceded by cvv/cvc)
    redacted = re.sub(r"(?i)\b(cvv|cvc)\s*(?:is|[:=-])?\s*(\d{3,4})\b", r"\1: [REDACTED_CVV]", redacted)
    
    # Redact OTP / Verification codes
    redacted = re.sub(r"(?i)\b(otp|one\s*time\s*password|verification\s*code)\s*(?:is|[:=-])?\s*(\d{4,8})\b", r"\1: [REDACTED_OTP]", redacted)
    
    # Redact UPI PINs / ATM PINs
    redacted = re.sub(r"(?i)\b(upi\s*pin|atm\s*pin|mpin)\s*(?:is|[:=-])?\s*(\d{4,6})\b", r"\1: [REDACTED_PIN]", redacted)
    
    # Redact Passwords
    redacted = re.sub(r"(?i)\b(password|passwd|pwd)\s*(?:is|[:=-])?\s*([^\s]{1,256})", r"\1: [REDACTED_PASSWORD]", redacted)
    
    # Redact full credit/debit card numbers (16 digits)
    redacted = re.sub(r"\b(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b", r"[REDACTED_CARD_NUMBER]", redacted)
    
    # Redact 12-digit Aadhaar numbers
    redacted = re.sub(r"\b(\d{4}\s\d{4}\s\d{4}|\d{12})\b", r"[REDACTED_AADHAAR]", redacted)
    
    # PAN identifiers and email/phone identifiers are retained only where required
    # for identity investigation. Financial credentials are never sent to providers.
    redacted = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[REDACTED_PAN]", redacted)
    return redacted

def redact_sensitive_patterns(text: str) -> str:
    """Test and convenience alias for redact_sensitive_credentials."""
    return redact_sensitive_credentials(text)
