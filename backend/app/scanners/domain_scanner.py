import socket
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from app.core.config import settings
import dns.resolver

# Known historical domains database for deterministic intelligence & demo speed
KNOWN_DOMAIN_INTELLIGENCE = {
    "microsoft.com": {
        "age_days": 12500,
        "created_date": "1991-05-02T00:00:00Z",
        "registrar": "MarkMonitor Inc.",
        "nameservers": ["ns1-07.azure-dns.com", "ns2-07.azure-dns.net"],
        "has_mx": True,
        "has_spf": True,
        "has_dmarc": True,
        "is_reputable": True
    },
    "google.com": {
        "age_days": 10500,
        "created_date": "1997-09-15T00:00:00Z",
        "registrar": "MarkMonitor Inc.",
        "nameservers": ["ns1.google.com", "ns2.google.com"],
        "has_mx": True,
        "has_spf": True,
        "has_dmarc": True,
        "is_reputable": True
    },
    "tcs.com": {
        "age_days": 9800,
        "created_date": "1998-01-20T00:00:00Z",
        "registrar": "Network Solutions LLC",
        "nameservers": ["ns1.tcs.com", "ns2.tcs.com"],
        "has_mx": True,
        "has_spf": True,
        "has_dmarc": True,
        "is_reputable": True
    },
    "infosys.com": {
        "age_days": 10200,
        "created_date": "1996-03-12T00:00:00Z",
        "registrar": "CSC Corporate Domains",
        "nameservers": ["dns1.cscdns.net", "dns2.cscdns.net"],
        "has_mx": True,
        "has_spf": True,
        "has_dmarc": True,
        "is_reputable": True
    },
    # Seeded fake / suspicious demo domains
    "microsoft-careers-india.xyz": {
        "age_days": 11,
        "created_date": (datetime.now(timezone.utc) - timedelta(days=11)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "registrar": "NameCheap Inc. / Privacy Protect Ltd",
        "nameservers": ["ns1.suspicious-host.xyz", "ns2.suspicious-host.xyz"],
        "has_mx": False,
        "has_spf": False,
        "has_dmarc": False,
        "is_reputable": False,
        "notes": "Suspicious youth (< 30 days old) claiming enterprise affiliation"
    },
    "scholarship-portal-gov.online": {
        "age_days": 6,
        "created_date": (datetime.now(timezone.utc) - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "registrar": "Hostinger Operations, UAB",
        "nameservers": ["ns1.dns-parking.com", "ns2.dns-parking.com"],
        "has_mx": False,
        "has_spf": False,
        "has_dmarc": False,
        "is_reputable": False
    },
    "quick-internships-direct.top": {
        "age_days": 3,
        "created_date": (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "registrar": "Alibaba Cloud Computing",
        "nameservers": ["dns1.hichina.com", "dns2.hichina.com"],
        "has_mx": False,
        "has_spf": False,
        "has_dmarc": False,
        "is_reputable": False
    }
}

def analyze_domain_intelligence(domain_name: str, synthetic: bool = False) -> Dict[str, Any]:
    """
    Performs domain intelligence gathering:
    - Age & creation dates
    - Registrar & nameservers
    - DNS records (A, MX, TXT)
    - SPF and DMARC posture
    - Youth risk analysis
    """
    domain_clean = domain_name.lower().strip()
    
    # Check seeded known / demo registry first
    if synthetic and domain_clean in KNOWN_DOMAIN_INTELLIGENCE:
        info = KNOWN_DOMAIN_INTELLIGENCE[domain_clean].copy()
        age_days = info["age_days"]
        flags = []
        if age_days < 30:
            flags.append({
                "code": "RECENTLY_REGISTERED_DOMAIN",
                "severity": "critical" if age_days < 14 else "high",
                "message": f"Domain is brand new (registered only {age_days} days ago).",
                "detail": "Fraudulent campaigns commonly deploy disposable domains that operate for only days or weeks before being abandoned."
            })
        if not info["has_mx"]:
            flags.append({
                "code": "MISSING_MX_RECORDS",
                "severity": "moderate",
                "message": "Domain lacks configured Mail Exchange (MX) records.",
                "detail": "Legitimate enterprise organizations maintain MX records for standard corporate communication."
            })
        if not info["has_dmarc"] or not info["has_spf"]:
            flags.append({
                "code": "DEFICIENT_EMAIL_AUTHENTICATION",
                "severity": "moderate",
                "message": "Missing SPF / DMARC authentication records on domain.",
                "detail": "Without SPF/DMARC, attackers can forge emails appearing to originate from this domain."
            })
            
        info["flags"] = flags
        info["domain"] = domain_clean
        info["is_demo_source"] = True
        return info

    if not settings.NETWORK_SCANNERS_ENABLED:
        return {"domain": domain_clean, "age_days": None, "created_date": None,
                "registrar": None, "nameservers": [], "dns_records": {}, "has_mx": False,
                "has_spf": False, "has_dmarc": False, "is_reputable": False,
                "flags": [], "is_demo_source": False, "status": "UNAVAILABLE"}

    # Live DNS Query with safe timeout
    dns_records = {"A": [], "MX": [], "TXT": [], "NS": []}
    has_mx = False
    has_spf = False
    has_dmarc = False
    nameservers = []
    
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 2.0
    
    try:
        answers_a = resolver.resolve(domain_clean, 'A')
        dns_records["A"] = [r.to_text() for r in answers_a]
    except Exception:
        pass
        
    try:
        answers_mx = resolver.resolve(domain_clean, 'MX')
        dns_records["MX"] = [r.exchange.to_text().rstrip('.') for r in answers_mx]
        has_mx = len(dns_records["MX"]) > 0
    except Exception:
        pass
        
    try:
        answers_ns = resolver.resolve(domain_clean, 'NS')
        nameservers = [r.target.to_text().rstrip('.') for r in answers_ns]
        dns_records["NS"] = nameservers
    except Exception:
        pass
        
    try:
        answers_txt = resolver.resolve(domain_clean, 'TXT')
        for r in answers_txt:
            txt_str = r.to_text().strip('"')
            dns_records["TXT"].append(txt_str)
            if "v=spf1" in txt_str.lower():
                has_spf = True
    except Exception:
        pass
        
    try:
        answers_dmarc = resolver.resolve(f"_dmarc.{domain_clean}", 'TXT')
        for r in answers_dmarc:
            if "v=dmarc1" in r.to_text().lower():
                has_dmarc = True
    except Exception:
        pass

    # DNS records do not establish domain age. Missing DNS may be a timeout.
    estimated_age = None
    flags = []
    return {
        "domain": domain_clean,
        "age_days": estimated_age,
        "created_date": None,
        "registrar": None,
        "nameservers": nameservers,
        "dns_records": dns_records,
        "has_mx": has_mx,
        "has_spf": has_spf,
        "has_dmarc": has_dmarc,
        "is_reputable": has_mx and has_spf and bool(dns_records["A"]),
        "flags": flags,
        "is_demo_source": False,
        "status": "COMPLETED" if dns_records["A"] else "UNAVAILABLE"
    }
