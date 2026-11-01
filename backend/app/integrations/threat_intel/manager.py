import asyncio
from typing import Dict, Any, List
from app.integrations.threat_intel.providers import (
    GoogleSafeBrowsingAdapter,
    VirusTotalAdapter,
    URLhausAdapter,
    DemoIntelligenceAdapter,
)

class ThreatIntelManager:
    def __init__(self):
        self.providers = [
            GoogleSafeBrowsingAdapter(),
            VirusTotalAdapter(),
            URLhausAdapter(),
            DemoIntelligenceAdapter(),
        ]

    async def aggregate_threat_intelligence(self, target: str, synthetic: bool = False) -> Dict[str, Any]:
        """
        Queries all configured threat intelligence providers in parallel with timeout.
        Aggregates flags and reports partial availability if any external API fails or is not configured.
        """
        results: List[Dict[str, Any]] = []
        is_flagged = False
        threat_types = []
        is_partial = False
        demo_used = False
        
        live_flagged = False
        for provider in self.providers:
            if isinstance(provider, DemoIntelligenceAdapter) and not synthetic:
                continue
            try:
                res = await asyncio.wait_for(provider.check_url_or_domain(target), timeout=3.0)
                results.append(res)
                if res["status"] == "FLAGGED":
                    is_flagged = True
                    if not res.get("is_demo_intelligence"):
                        live_flagged = True
                    if res.get("threat_type"):
                        threat_types.append(f"{provider.name}: {res['threat_type']}")
                elif res["status"] == "UNAVAILABLE":
                    is_partial = True
                if res.get("is_demo_intelligence"):
                    demo_used = True
            except Exception as e:
                is_partial = True
                results.append({
                    "provider": provider.name,
                    "status": "UNAVAILABLE",
                    "threat_type": None,
                    "is_demo_intelligence": False,
                    "details": {"error": "Provider timeout or network error"}
                })
                
        summary_note = "Threat intelligence lookup complete across active providers."
        if is_partial and not is_flagged:
            summary_note = "Partial analysis — some external intelligence providers were unconfigured or unavailable."
            
        return {
            "is_flagged": is_flagged,
            "live_flagged": live_flagged,
            "threat_summary": threat_types[0] if threat_types else ("No known threat signatures detected" if not is_partial else "Partial checks complete"),
            "threat_types": threat_types,
            "provider_results": results,
            "is_partial": is_partial,
            "demo_intelligence_applied": demo_used,
            "summary_note": summary_note
        }

threat_intel_manager = ThreatIntelManager()
