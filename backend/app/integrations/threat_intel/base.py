from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ThreatIntelligenceProvider(ABC):
    """Abstract base class for all threat intelligence service providers"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
        
    @property
    @abstractmethod
    def is_configured(self) -> bool:
        pass
        
    @abstractmethod
    async def check_url_or_domain(self, target: str) -> Dict[str, Any]:
        """
        Queries provider for threat classification on given URL or domain.
        Returns dict with:
        {
            "provider": str,
            "status": "FLAGGED" | "CLEAN" | "UNKNOWN" | "UNAVAILABLE",
            "threat_type": Optional[str],
            "is_demo_intelligence": bool,
            "details": Dict[str, Any]
        }
        """
        pass
