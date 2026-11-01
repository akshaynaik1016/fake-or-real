import re
from typing import Dict, Any, List, Optional

# Verified corporate organizations and government/institutional entities
VERIFIED_ORGANIZATIONS_REGISTRY: Dict[str, Dict[str, Any]] = {
    "bel": {
        "canonical_name":"Bharat Electronics Limited","official_domains":["bel-india.in"],
        "official_careers_url":"https://bel-india.in/job-notifications/","primary_country":"India",
        "corporate_identifier":None,"aliases":["bharat electronics limited","bharat electronics ltd","bharat electronics"],
        "reference_url":"https://www.indiascienceandtechnology.gov.in/allstinstitutions/bharat-electronics-limited-bel",
        "reference_scope":"Organization website reference only; no recruitment advertisement or payment authorization verified."
    },
    "microsoft": {
        "canonical_name": "Microsoft Corporation",
        "official_domains": ["microsoft.com", "careers.microsoft.com", "linkedin.com/company/microsoft"],
        "official_careers_url": "https://careers.microsoft.com",
        "primary_country": "United States / Global",
        "corporate_identifier": "US-SEC-0000789019",
        "aliases": ["microsoft", "microsoft india", "msft", "microsoft technologies", "microsoft ai"]
    },
    "google": {
        "canonical_name": "Google LLC / Alphabet Inc.",
        "official_domains": ["google.com", "careers.google.com", "google.co.in"],
        "official_careers_url": "https://careers.google.com",
        "primary_country": "United States / Global",
        "corporate_identifier": "US-SEC-0001652044",
        "aliases": ["google", "google india", "alphabet", "google cloud"]
    },
    "amazon": {
        "canonical_name": "Amazon.com, Inc.",
        "official_domains": ["amazon.com", "amazon.jobs", "amazon.in"],
        "official_careers_url": "https://amazon.jobs",
        "primary_country": "United States / Global",
        "corporate_identifier": "US-SEC-0001018724",
        "aliases": ["amazon", "amazon web services", "aws", "amazon india"]
    },
    "tcs": {
        "canonical_name": "Tata Consultancy Services Limited",
        "official_domains": ["tcs.com", "nextstep.tcs.com", "careers.tcs.com"],
        "official_careers_url": "https://nextstep.tcs.com",
        "primary_country": "India",
        "corporate_identifier": "CIN: L22210MH1995PLC084781 (MCA / ROC Mumbai)",
        "aliases": ["tcs", "tata consultancy services", "tata consultancy", "tcs ion", "tcs nextstep"]
    },
    "infosys": {
        "canonical_name": "Infosys Limited",
        "official_domains": ["infosys.com", "career.infosys.com", "infy.com"],
        "official_careers_url": "https://career.infosys.com",
        "primary_country": "India",
        "corporate_identifier": "CIN: L85110KA1981PLC013115 (MCA / ROC Bangalore)",
        "aliases": ["infosys", "infosys limited", "infy", "infosys springboard"]
    },
    "wipro": {
        "canonical_name": "Wipro Limited",
        "official_domains": ["wipro.com", "careers.wipro.com"],
        "official_careers_url": "https://careers.wipro.com",
        "primary_country": "India",
        "corporate_identifier": "CIN: L32102KA1945PLC020800 (MCA / ROC Bangalore)",
        "aliases": ["wipro", "wipro limited", "wipro technologies"]
    },
    "isro": {
        "canonical_name": "Indian Space Research Organisation",
        "official_domains": ["isro.gov.in", "nrsc.gov.in", "sac.gov.in"],
        "official_careers_url": "https://www.isro.gov.in/Careers.html",
        "primary_country": "India",
        "corporate_identifier": "Govt of India Department of Space",
        "aliases": ["isro", "indian space research organisation"]
    },
    "drdo": {
        "canonical_name": "Defence Research and Development Organisation",
        "official_domains": ["drdo.gov.in", "rac.gov.in"],
        "official_careers_url": "https://rac.gov.in",
        "primary_country": "India",
        "corporate_identifier": "Govt of India Ministry of Defence",
        "aliases": ["drdo", "rac drdo"]
    }
}

def organization_mentions(text: str) -> list[dict]:
    """Extract claimed names, separate from the small bundled reference registry.

    Unknown names need an explicit organization label or a distinctive business
    heading. No filename, email-domain-to-company guess or OCR character repair.
    """
    candidates=[]
    def add(start,end,method):
        raw=text[start:end];value=re.sub(r'\s+',' ',raw).strip()
        if len(value)<2:return
        ref=next((o for o in VERIFIED_ORGANIZATIONS_REGISTRY.values() if value.casefold() in
                  [o['canonical_name'].casefold(),*[a.casefold() for a in o['aliases']]]),None)
        candidates.append({'canonical_name':ref['canonical_name'] if ref else value,
            'start':start,'end':end,'excerpt':raw,'extraction_method':method,
            'verification_status':'CLAIMED','reference':ref})
    for m in re.finditer(r'(?im)^\s*(?:organization|organisation|company|employer|organized by|organisation name|company name)\s*:\s*([^\n.;]{2,150})',text):
        add(m.start(1),m.end(1),'explicit_organization_label')
    # Business suffix and a short standalone heading reduce slogan false positives.
    for m in re.finditer(r'(?m)^[ \t]*([A-Z][A-Z0-9&.-]*(?:[ \t]+[A-Z][A-Z0-9&.-]*){0,4}[ \t]+(?:TECH|TECHNOLOGIES|SOLUTIONS|SYSTEMS|LABS|FOUNDATION|PVT[.]? LTD[.]?|LIMITED|INC[.]?))[ \t]*$',text):
        if not re.search(r'\b(?:JOIN|APPLY|HIRING|INTERNSHIP|PROGRAM|WELCOME|OUR|YOUR)\b',m.group(1)):
            add(m.start(1),m.end(1),'business_heading')
    for org in VERIFIED_ORGANIZATIONS_REGISTRY.values():
        matches=[m for alias in org['aliases'] for m in re.finditer(r'\b'+re.escape(alias)+r'\b',text,re.I)]
        if matches:
            m=min(matches,key=lambda x:x.start())
            # Explicit company labels take precedence over unrelated brand mentions.
            if not candidates:add(m.start(),m.end(),'bundled_name_reference')
    unique={}
    for c in candidates:unique.setdefault((c['start'],c['end']),c)
    return sorted(unique.values(),key=lambda c:c['start'])


def identify_claimed_organization(text: str) -> Optional[Dict[str, Any]]:
    mentions=organization_mentions(text)
    if not mentions:return None
    first=mentions[0]
    return {**(first['reference'] or {}),**first}

def verify_organization_domain_match(claimed_org_name: str, domain_name: str) -> Dict[str, Any]:
    """
    Evaluates whether the claimed organization owns or is officially associated with
    the submitted domain name.
    Detects CRITICAL IDENTITY MISMATCH.
    """
    clean_domain = domain_name.lower().strip()
    org_key = None
    org_data = None
    
    # Resolve organization record
    claimed_lower = claimed_org_name.lower().strip()
    for key, data in VERIFIED_ORGANIZATIONS_REGISTRY.items():
        if claimed_lower in [key,data['canonical_name'].casefold(),*[a.casefold() for a in data['aliases']]]:
            org_key = key
            org_data = data
            break
            
    if not org_data:
        # Organization not in primary global registry; return neutral verification status
        return {
            "status": "UNVERIFIED_INDEPENDENT",
            "verified": False,
            "claimed_organization": claimed_org_name,
            "canonical_name": claimed_org_name,
            "official_domains": [],
            "corporate_identifier": None,
            "mismatch": False,
            "explanation": f"'{claimed_org_name}' is not currently indexed in the bundled organization reference list. Independent manual verification of domain ownership is recommended.",
            "severity": "moderate"
        }
        
    # Check if the submitted domain is an official domain or subdomain of an official domain
    is_domain_match = False
    for off_domain in org_data["official_domains"]:
        if clean_domain == off_domain or clean_domain.endswith(f".{off_domain}"):
            is_domain_match = True
            break
            
    if is_domain_match:
        return {
            "status": "VERIFIED_OFFICIAL_MATCH",
            "verified": True,
            "claimed_organization": claimed_org_name,
            "canonical_name": org_data["canonical_name"],
            "official_domains": org_data["official_domains"],
            "official_careers_url": org_data.get("official_careers_url"),
            "corporate_identifier": org_data.get("corporate_identifier"),
            "mismatch": False,
            "explanation": f"Domain '{clean_domain}' matches official corporate domain infrastructure for {org_data['canonical_name']}.",
            "severity": "verified"
        }
    else:
        # Mismatch detected
        return {
            "status": "CRITICAL_IDENTITY_MISMATCH",
            "verified": False,
            "claimed_organization": claimed_org_name,
            "canonical_name": org_data["canonical_name"],
            "official_domains": org_data["official_domains"],
            "official_careers_url": org_data.get("official_careers_url"),
            "corporate_identifier": org_data.get("corporate_identifier"),
            "mismatch": True,
            "explanation": f"The submitted opportunity claims to represent {org_data['canonical_name']}, but the analyzed domain '{clean_domain}' could not be independently associated with {org_data['canonical_name']}'s official domain infrastructure.",
            "severity": "critical"
        }

def verify_organization_match(claimed_org_name: str, domain_name: str) -> Dict[str, Any]:
    """Test and convenience alias for organization domain verification."""
    res = verify_organization_domain_match(claimed_org_name, domain_name)
    if res["verified"]:
        status = "VERIFIED"
    elif res["mismatch"]:
        status = "CRITICAL_MISMATCH"
    else:
        status = "UNVERIFIED"
        
    return {
        "status": status,
        "claimed_org": claimed_org_name,
        "is_official": res["verified"],
        "explanation": res["explanation"],
        "details": res
    }
