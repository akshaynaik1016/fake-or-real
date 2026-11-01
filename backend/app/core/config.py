import os
import secrets
from typing import List, Dict
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "FAKE OR REAL - Evidence-Based Digital Trust & Safety Platform"
    TAGLINE: str = "Don't trust. Verify."
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security & Auth
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    JWT_SECRET: str = os.getenv("JWT_SECRET") or secrets.token_urlsafe(48)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fake_or_real.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [o.strip() for o in os.getenv(
        "BACKEND_CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(",") if o.strip()]
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "none")
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "8"))
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    RESEARCH_TIMEOUT_SECONDS: float = float(os.getenv("RESEARCH_TIMEOUT_SECONDS", "8"))
    MAX_RESEARCH_CALLS: int = 3
    CASE_MAX_URLS: int = int(os.getenv("CASE_MAX_URLS", "10"))
    CASE_MAX_PDFS: int = int(os.getenv("CASE_MAX_PDFS", "10"))
    OFFICIAL_NOTICE_FETCH_ENABLED: bool = os.getenv("OFFICIAL_NOTICE_FETCH_ENABLED", "false").lower() == "true"
    CASE_URL_FETCH_ENABLED: bool = os.getenv("CASE_URL_FETCH_ENABLED", "false").lower() == "true"
    NETWORK_SCANNERS_ENABLED: bool = os.getenv("NETWORK_SCANNERS_ENABLED", "false").lower() == "true"
    
    # External Threat Intel APIs (Gracefully optional)
    SAFE_BROWSING_API_KEY: str = os.getenv("SAFE_BROWSING_API_KEY", "")
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Demo & Mock Intelligence Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    # Configurable Scoring Weights (Must sum to 100)
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "url_security": 0.15,
        "domain_intelligence": 0.10,
        "organization_verification": 0.15,
        "email_security": 0.10,
        "threat_intelligence": 0.15,
        "content_analysis": 0.10,
        "payment_risk": 0.10,
        "identity_verification": 0.05,
        "document_analysis": 0.05,
        "community_reports": 0.05,
    }
    
    # Upload limits
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: List[str] = [".png", ".jpg", ".jpeg", ".webp", ".pdf", ".txt", ".eml"]

settings = Settings()
if "*" in settings.BACKEND_CORS_ORIGINS:
    raise ValueError("CORS origins must be explicit")
if settings.ENVIRONMENT == "production":
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32 or "super-secret" in secret or "change-me" in secret:
        raise ValueError("Production requires a unique JWT_SECRET of at least 32 characters")
    if settings.DEMO_MODE:
        raise ValueError("Production requires DEMO_MODE=false")
