import re
import math
from urllib.parse import urlparse
from typing import Dict, Any, List

SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "buzz", "club", "work", "gq", "cf", "ml", "ga", "fit", "cc",
    "surf", "rest", "cam", "loan", "stream", "live", "link", "download", "racing"
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "buff.ly", "ow.ly", "cutt.ly",
    "rebrand.ly", "shorturl.at", "tiny.cc", "v.gd"
}

POPULAR_BRANDS = [
    "google", "microsoft", "amazon", "apple", "facebook", "meta", "netflix", "paypal",
    "infosys", "tcs", "wipro", "reliance", "tatamotors", "statebank", "sbi", "hdfc", "icici",
    "linkedin", "instagram", "telegram", "whatsapp", "dropbox", "github"
]

def calculate_shannon_entropy(string: str) -> float:
    """Calculate the Shannon entropy of a string (higher entropy = more random/suspicious)"""
    if not string:
        return 0.0
    prob = [float(string.count(c)) / len(string) for c in dict.fromkeys(list(string))]
    entropy = -sum([p * math.log(p) / math.log(2.0) for p in prob])
    return entropy

def extract_registrable_domain(hostname: str) -> Dict[str, str]:
    """
    Extracts the actual registrable domain from a hostname.
    E.g. 'google.com.security-check.example.xyz' -> registrable: 'example.xyz'
    """
    parts = hostname.lower().split('.')
    if len(parts) <= 2:
        return {"subdomain": "", "registrable_domain": hostname.lower()}
    
    # Handle two-part ccTLDs like .co.uk, .com.in, .ac.in
    if len(parts) >= 3 and parts[-2] in ["co", "com", "ac", "gov", "edu", "org", "net"] and len(parts[-1]) == 2:
        registrable = ".".join(parts[-3:])
        subdomain = ".".join(parts[:-3])
    else:
        registrable = ".".join(parts[-2:])
        subdomain = ".".join(parts[:-2])
        
    return {"subdomain": subdomain, "registrable_domain": registrable}

def analyze_url_security(raw_url: str) -> Dict[str, Any]:
    """
    Performs full URL security analysis:
    - Hostname extraction
    - Actual registrable domain isolation
    - HTTPS check
    - IP-based URL detection
    - Suspicious TLD check
    - Punycode / IDN homograph check
    - Lookalike brand impersonation
    - URL shortening detection
    - Subdomain abuse analysis
    - Entropy analysis
    """
    if not raw_url.startswith(("http://", "https://")):
        raw_url = "https://" + raw_url
        
    parsed = urlparse(raw_url)
    hostname = parsed.hostname or ""
    scheme = parsed.scheme.lower()
    path = parsed.path
    query = parsed.query
    
    flags = []
    is_https = scheme == "https"
    
    domain_info = extract_registrable_domain(hostname)
    reg_domain = domain_info["registrable_domain"]
    subdomain = domain_info["subdomain"]
    tld = reg_domain.split('.')[-1] if '.' in reg_domain else ""
    
    # 1. HTTPS Check
    if not is_https:
        flags.append({
            "code": "INSECURE_HTTP",
            "severity": "high",
            "message": "URL uses unencrypted HTTP instead of HTTPS.",
            "detail": "Data in transit is susceptible to interception and tampering."
        })
        
    # 2. IP-based URL
    ip_pattern = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
    is_ip_url = bool(re.match(ip_pattern, hostname))
    if is_ip_url:
        flags.append({
            "code": "IP_BASED_URL",
            "severity": "critical",
            "message": f"URL uses raw IP address '{hostname}' rather than a verified domain name.",
            "detail": "Legitimate organizations almost never host public opportunities on bare IP addresses."
        })
        
    # 3. Suspicious TLD
    is_suspicious_tld = tld in SUSPICIOUS_TLDS
    if is_suspicious_tld:
        flags.append({
            "code": "SUSPICIOUS_TLD",
            "severity": "moderate",
            "message": f"Domain uses '.{tld}' top-level domain frequently associated with low-cost or throwaway registrations.",
            "detail": f"Registration on '.{tld}' requires extra identity verification."
        })
        
    # 4. Punycode / Homograph Attack
    has_punycode = "xn--" in hostname
    if has_punycode:
        flags.append({
            "code": "PUNYCODE_HOMOGRAPH",
            "severity": "critical",
            "message": f"Hostname contains internationalized Punycode ('{hostname}').",
            "detail": "Punycode is frequently used in visual spoofing / homograph attacks to mimic trusted brands."
        })
        
    # 5. Shortener
    is_shortener = reg_domain in SHORTENER_DOMAINS
    if is_shortener:
        flags.append({
            "code": "URL_SHORTENER",
            "severity": "moderate",
            "message": f"URL uses shortening service '{reg_domain}' which obscures the final destination.",
            "detail": "Attackers disguise malicious targets behind shortened redirect links."
        })
        
    # 6. Lookalike Brand Impersonation in Subdomain or Domain
    brand_impersonation = None
    for brand in POPULAR_BRANDS:
        # If brand is in subdomain or registrable domain, but registrable domain is NOT the official brand domain
        if brand in hostname:
            expected_official = f"{brand}.com"
            if reg_domain != expected_official and not reg_domain.endswith(f".{brand}.com"):
                brand_impersonation = brand
                flags.append({
                    "code": "BRAND_LOOKALIKE_IMPERSONATION",
                    "severity": "critical",
                    "message": f"Potential impersonation of '{brand.capitalize()}'. Actual registrable domain is '{reg_domain}', NOT official '{expected_official}'.",
                    "detail": f"The URL deceptively features the brand name '{brand}' in its subdomain or host '{hostname}' to mislead users."
                })
                break
                
    # 7. Excessive Subdomains
    subdomain_parts = subdomain.split('.') if subdomain else []
    if len(subdomain_parts) >= 3:
        flags.append({
            "code": "EXCESSIVE_SUBDOMAINS",
            "severity": "moderate",
            "message": f"Hostname contains {len(subdomain_parts)} nested subdomains ('{subdomain}').",
            "detail": "Attackers chain subdomains to push the true domain name off-screen on mobile viewports."
        })
        
    # Generate standard indicators list
    indicators = []
    for f in flags:
        ind_title = f["code"].replace("_", " ").title()
        if "BRAND_LOOKALIKE" in f["code"]:
            ind_title = "Lookalike Brand Impersonation"
        elif "SUSPICIOUS_TLD" in f["code"]:
            ind_title = "Suspicious TLD (.xyz / .top)"
        elif "EXCESSIVE_SUBDOMAINS" in f["code"]:
            ind_title = "Excessive Subdomains Spoofing"
        elif "INSECURE_HTTP" in f["code"]:
            ind_title = "Unencrypted HTTP"
        indicators.append({
            "indicator": ind_title,
            "severity": f["severity"],
            "detail": f["message"]
        })

    excessive_subdomains = len(subdomain_parts) >= 3
    url_entropy = calculate_shannon_entropy(raw_url)

    result = {
        "raw_url": raw_url,
        "scheme": scheme,
        "is_https": is_https,
        "hostname": hostname,
        "registrable_domain": reg_domain,
        "subdomain": subdomain,
        "tld": tld,
        "is_ip_url": is_ip_url,
        "is_shortener": is_shortener,
        "is_suspicious_tld": is_suspicious_tld,
        "has_punycode": has_punycode,
        "brand_impersonation": brand_impersonation,
        "excessive_subdomains": excessive_subdomains,
        "entropy": round(url_entropy, 2),
        "flags": flags,
        "indicators": indicators
    }
    return result

def analyze_url_structure(raw_url: str) -> Dict[str, Any]:
    """Alias for test compatibility and URL structural dissection."""
    return analyze_url_security(raw_url)
