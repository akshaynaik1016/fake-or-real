import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.integrations.threat_intel.base import ThreatIntelligenceProvider

# Demo threat database for offline hackathon demonstration
DEMO_FLAGGED_TARGETS = {
    "microsoft-careers-india.xyz": {
        "status": "FLAGGED",
        "threat_type": "Social Engineering / Brand Impersonation",
        "details": {
            "reputation_score": 12,
            "community_votes_malicious": 14,
            "category": "Fake Internship / Phishing",
            "first_seen": "11 days ago"
        }
    },
    "scholarship-portal-gov.online": {
        "status": "FLAGGED",
        "threat_type": "Financial Advance Fee Fraud",
        "details": {
            "reputation_score": 8,
            "community_votes_malicious": 22,
            "category": "Fake Scholarship Application Fee",
            "first_seen": "6 days ago"
        }
    },
    "quick-internships-direct.top": {
        "status": "FLAGGED",
        "threat_type": "Malicious Redirect / Credential Harvesting",
        "details": {
            "reputation_score": 5,
            "community_votes_malicious": 19,
            "category": "Phishing",
            "first_seen": "3 days ago"
        }
    },
    "microsoft.com": {
        "status": "CLEAN",
        "threat_type": None,
        "details": {
            "reputation_score": 100,
            "community_votes_malicious": 0,
            "category": "Legitimate Enterprise Infrastructure"
        }
    },
    "google.com": {
        "status": "CLEAN",
        "threat_type": None,
        "details": {
            "reputation_score": 100,
            "community_votes_malicious": 0,
            "category": "Legitimate Enterprise Infrastructure"
        }
    }
}


class GoogleSafeBrowsingAdapter(ThreatIntelligenceProvider):
    @property
    def name(self) -> str:
        return "Google Safe Browsing API v4"

    @property
    def is_configured(self) -> bool:
        return bool(settings.SAFE_BROWSING_API_KEY)

    async def check_url_or_domain(self, target: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.name,
                "status": "UNAVAILABLE",
                "threat_type": None,
                "is_demo_intelligence": False,
                "details": {"message": "Google Safe Browsing API key not configured in .env"}
            }
        
        try:
            url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={settings.SAFE_BROWSING_API_KEY}"
            payload = {
                "client": {"clientId": "fake-or-real", "clientVersion": "1.0.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": target}]
                }
            }
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    matches = data.get("matches", [])
                    if matches:
                        return {
                            "provider": self.name,
                            "status": "FLAGGED",
                            "threat_type": matches[0].get("threatType", "SOCIAL_ENGINEERING"),
                            "is_demo_intelligence": False,
                            "details": matches[0]
                        }
                    return {
                        "provider": self.name,
                        "status": "CLEAN",
                        "threat_type": None,
                        "is_demo_intelligence": False,
                        "details": {"message": "No active threat matches found."}
                    }
                return {"provider": self.name, "status": "UNAVAILABLE", "threat_type": None,
                        "is_demo_intelligence": False, "details": {"message": "Provider returned an error"}}
        except Exception as e:
            return {
                "provider": self.name,
                "status": "UNAVAILABLE",
                "threat_type": None,
                "is_demo_intelligence": False,
                "details": {"error": "Provider request unavailable"}
            }


class VirusTotalAdapter(ThreatIntelligenceProvider):
    @property
    def name(self) -> str:
        return "VirusTotal Threat Intelligence"

    @property
    def is_configured(self) -> bool:
        return bool(settings.VIRUSTOTAL_API_KEY)

    async def check_url_or_domain(self, target: str) -> Dict[str, Any]:
        if not self.is_configured:
            return {
                "provider": self.name,
                "status": "UNAVAILABLE",
                "threat_type": None,
                "is_demo_intelligence": False,
                "details": {"message": "VirusTotal API key not configured in .env"}
            }
        return {"provider": self.name, "status": "UNAVAILABLE", "threat_type": None,
                "is_demo_intelligence": False, "details": {"message": "Live adapter not implemented"}}


class URLhausAdapter(ThreatIntelligenceProvider):
    @property
    def name(self) -> str:
        return "Abuse.ch URLhaus"

    @property
    def is_configured(self) -> bool:
        return True # URLhaus has a public free query endpoint

    async def check_url_or_domain(self, target: str) -> Dict[str, Any]:
        return {"provider": self.name, "status": "UNAVAILABLE", "threat_type": None,
                "is_demo_intelligence": False, "details": {"message": "Live adapter not implemented"}}


class DemoIntelligenceAdapter(ThreatIntelligenceProvider):
    @property
    def name(self) -> str:
        return "Demo Intelligence (Offline Fallback Engine)"

    @property
    def is_configured(self) -> bool:
        return True

    async def check_url_or_domain(self, target: str) -> Dict[str, Any]:
        clean_host = target.replace("https://", "").replace("http://", "").split("/")[0].lower()
        
        match = DEMO_FLAGGED_TARGETS.get(clean_host)
        if match:
            return {
                "provider": self.name,
                "status": match["status"],
                "threat_type": match["threat_type"],
                "is_demo_intelligence": True,
                "label": "Demo Intelligence",
                "details": match["details"]
            }
            
        return {
            "provider": self.name,
            "status": "CLEAN",
            "threat_type": None,
            "is_demo_intelligence": True,
            "label": "Demo Intelligence",
            "details": {"message": "No threats recorded in local demo repository."}
        }
