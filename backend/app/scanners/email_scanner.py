import re
from typing import Dict, Any, List, Optional
from email import message_from_string

FREE_WEBMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "ymail.com", "outlook.com", "hotmail.com", "live.com",
    "aol.com", "icloud.com", "mail.com", "proton.me", "protonmail.com", "zoho.com"
}

ENTERPRISE_KEYWORDS = [
    "hr", "recruiter", "talent", "careers", "hiring", "interviews", "jobs", "officer",
    "microsoft", "google", "amazon", "apple", "tcs", "infosys", "wipro", "ibm"
]

def parse_email_sender(from_header: str) -> Dict[str, str]:
    """
    Parses 'Google HR <recruiter123@gmail.com>' into display_name and email_address.
    """
    match = re.match(r'^(.*?)\s*<([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)>', from_header.strip())
    if match:
        display_name = match.group(1).strip().strip('"').strip("'")
        email_addr = match.group(2).strip().lower()
        return {"display_name": display_name, "email": email_addr}
    
    # Just a bare email
    email_clean = from_header.strip().strip('<>').lower()
    return {"display_name": "", "email": email_clean}

def analyze_email_security(raw_email_or_headers: str) -> Dict[str, Any]:
    """
    Analyzes raw email content or header string.
    Checks:
    - Display name spoofing
    - Free webmail claiming enterprise affiliation
    - Reply-To mismatch
    - SPF/DKIM/DMARC headers if present
    """
    flags = []
    
    # Check if raw RFC 822 format or pasted text
    is_raw_eml = ("From:" in raw_email_or_headers or "Received:" in raw_email_or_headers)
    from_header = ""
    reply_to = ""
    subject = ""
    spf_result = "unknown"
    dkim_result = "unknown"
    dmarc_result = "unknown"
    
    if is_raw_eml:
        msg = message_from_string(raw_email_or_headers)
        from_header = msg.get("From", "")
        reply_to = msg.get("Reply-To", "")
        subject = msg.get("Subject", "")
        auth_results = msg.get("Authentication-Results", "").lower()
        if "spf=pass" in auth_results:
            spf_result = "pass"
        elif "spf=fail" in auth_results:
            spf_result = "fail"
            
        if "dkim=pass" in auth_results:
            dkim_result = "pass"
        elif "dkim=fail" in auth_results:
            dkim_result = "fail"
    else:
        # Search for From: in text
        match_from = re.search(r'(?i)from:\s*([^\r\n]+)', raw_email_or_headers)
        if match_from:
            from_header = match_from.group(1)
        else:
            # Look for any email address
            match_any_email = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', raw_email_or_headers)
            if match_any_email:
                from_header = match_any_email.group(1)
                
    parsed_sender = parse_email_sender(from_header) if from_header else {"display_name": "", "email": ""}
    sender_email = parsed_sender["email"]
    display_name = parsed_sender["display_name"]
    sender_domain = sender_email.split('@')[-1] if '@' in sender_email else ""
    
    is_free_webmail = sender_domain in FREE_WEBMAIL_DOMAINS
    
    # 1. Display Name vs Actual Address Spoofing
    if display_name:
        display_lower = display_name.lower()
        # Does display name claim an enterprise brand or HR role?
        from app.scanners.org_scanner import identify_claimed_organization
        has_enterprise_claim = bool(identify_claimed_organization(display_name))
        if has_enterprise_claim and is_free_webmail:
            flags.append({
                "code": "DISPLAY_NAME_ENTERPRISE_MISMATCH",
                "severity": "moderate",
                "message": f"Display Name claims '{display_name}' but sender is using personal/free webmail ({sender_email}).",
                "detail": "Sender identity could not be independently verified. A personal address alone does not prove impersonation; independent authorization remains unknown."
            })
            
    # 2. Reply-To Mismatch
    if reply_to and sender_email:
        parsed_reply = parse_email_sender(reply_to)
        if parsed_reply["email"] and parsed_reply["email"] != sender_email:
            flags.append({
                "code": "REPLY_TO_MISMATCH",
                "severity": "moderate",
                "message": f"Reply-To address ('{parsed_reply['email']}') differs from sender From address ('{sender_email}').",
                "detail": "Attackers configure mismatched Reply-To addresses to redirect responses to external mailboxes."
            })
            
    # 3. SPF / DKIM failure in headers
    if spf_result == "fail":
        flags.append({
            "code": "SPF_VALIDATION_FAILED",
            "severity": "moderate",
            "message": "Submitted headers report SPF failure; no independent SPF validation performed.",
            "detail": "Sending IP was not authorized by the domain's SPF policy."
        })
    if dkim_result == "fail":
        flags.append({
            "code": "DKIM_VALIDATION_FAILED",
            "severity": "moderate",
            "message": "Submitted headers report DKIM failure; no independent signature validation performed.",
            "detail": "Email contents may have been altered in transit or forged."
        })

    return {
        "from_header": from_header,
        "display_name": display_name,
        "sender_email": sender_email,
        "sender_domain": sender_domain,
        "is_free_webmail": is_free_webmail,
        "reply_to": reply_to,
        "subject": subject,
        "spf_status": spf_result,
        "dkim_status": dkim_result,
        "flags": flags
    }
