from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

# ----------------- Auth Schemas -----------------
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must fit within 72 UTF-8 bytes")
        return value

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----------------- Evidence & Risk Schemas -----------------
class EvidenceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    category: str
    severity: str # critical, high, moderate, low, verified
    evidence: str
    source: str
    confidence: float = 1.0
    explanation: Optional[str] = None
    timestamp: Optional[datetime] = None
    observed_value: Optional[str] = None
    origin: Optional[str] = None
    verification_status: Optional[str] = None
    correlation_group: Optional[str] = None
    related_entities: List[str] = Field(default_factory=list)
    source_spans: List[Dict[str, Any]] = Field(default_factory=list)
    source_id: Optional[str] = None
    original_excerpt: Optional[str] = None
    extracted_value: Any = None
    extraction_method: str = 'deterministic_rule'
    claim_type: Optional[str] = None
    provenance_kind: str = 'RULE_OUTPUT'
    verified_claim_id: Optional[str] = None
    verification_scope: Optional[str] = None
    fact_key: str | None = None
    occurrences: int = 1
    payment_context: dict | None = None
    citations: list[dict] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)

class RiskIndicatorItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: Optional[str] = None
    weight: float = 1.0
    is_positive: bool = False

class VerificationCheckItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    check_name: str # Organization, Domain, Email, Phone, SSL, Threat Intelligence, Payment, Document, Identity
    status: str     # passed, warning, failed
    details: Optional[str] = None

# ----------------- Scan Schemas -----------------
class ScanCreateRequest(BaseModel):
    input_type: Literal["url", "text", "screenshot", "pdf", "email", "phone", "org"]
    content: str = Field(min_length=1, max_length=50000)
    target_identifier: Optional[str] = Field(default=None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None

class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    input_type: str
    target_identifier: Optional[str] = None
    status: str
    trust_score: int | None
    risk_level: str
    analysis_confidence: int
    summary: Optional[str] = None
    created_at: datetime
    is_demo: bool = False
    assessment: Optional[Dict[str, Any]] = None

class TimelineEvent(BaseModel):
    timestamp_str: str
    step: str
    status: str # passed, warning, critical, info
    details: str

class ScanDetailResponse(ScanResponse):
    input_content: str
    evidence: List[EvidenceItem] = []
    indicators: List[RiskIndicatorItem] = []
    verification_results: List[VerificationCheckItem] = []
    recommended_actions: List[str] = []
    timeline: List[TimelineEvent] = []
    weights_used: Optional[Dict[str, float]] = None
    threat_intel_details: Optional[Dict[str, Any]] = None
    investigation: Optional[Dict[str, Any]] = None


# ----------------- Trust Passport & Reports -----------------
class TrustPassportResponse(BaseModel):
    scan_id: str
    opportunity_name: str
    organization: Optional[str]
    website: Optional[str]
    trust_score: int | None
    risk_level: str
    analysis_confidence: int
    verification_checks_passed: int
    total_verification_checks: int
    evidence_count: int
    qr_code_url: str
    last_analyzed: datetime
    verification_summary: str
    assessment: Optional[Dict[str, Any]] = None

class SavedReportResponse(BaseModel):
    id: str
    scan_id: str
    share_token: str
    title: str
    created_at: datetime
    report_data: Dict[str, Any]


# ----------------- Emergency Schemas -----------------
class EmergencyTriageRequest(BaseModel):
    incident_type: str # entered_password, entered_card, shared_otp, shared_upi_pin, sent_money, downloaded_file, shared_aadhaar_pan, opened_website
    details: Optional[str] = None
    urgency_level: Optional[str] = "immediate"

class EmergencyStep(BaseModel):
    order: int
    action: str
    priority: str # CRITICAL, HIGH, RECOMMENDED
    instructions: str
    official_contacts: Optional[List[str]] = None

class EmergencyGuidanceResponse(BaseModel):
    incident_type: str
    headline: str
    severity: str
    immediate_steps: List[EmergencyStep]
    helpline_numbers: Dict[str, str]
    caution_note: str


# ----------------- Community Schemas -----------------
class CommunityReportCreate(BaseModel):
    target_url: Optional[str] = None
    target_domain: Optional[str] = None
    target_phone: Optional[str] = None
    target_email: Optional[str] = None
    organization_name: Optional[str] = None
    scam_category: str # fake_internship, job_scam, phishing_website, payment_scam, fake_scholarship, impersonation
    description: str = Field(..., min_length=10)
    evidence_text: Optional[str] = None

class CommunityReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    scam_category: str
    organization_name: Optional[str] = None
    target_domain: Optional[str] = None
    description: str
    evidence_text: Optional[str] = None
    status: str
    upvotes: int
    created_at: datetime

class CommunityStats(BaseModel):
    total_reports: int
    scam_category_breakdown: Dict[str, int]
    top_reported_domains: List[Dict[str, Any]]
    recent_reports: List[CommunityReportResponse]


# ----------------- AI Chat Schemas -----------------
class AIChatRequest(BaseModel):
    scan_id: str
    question: str = Field(min_length=1, max_length=2000)

class AIChatResponse(BaseModel):
    answer: str
    grounded_in_evidence: bool
    evidence_referenced: List[str]
    confidence_note: str
    provider: str = "deterministic"
    mode: str = "FALLBACK"
    evidence_ids: List[str] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    context_revision: Optional[int] = None


# ----------------- Comparison Schemas -----------------
class ComparisonRequest(BaseModel):
    scan_id_a: str
    scan_id_b: str

class ComparisonResponse(BaseModel):
    opportunity_a: ScanDetailResponse
    opportunity_b: ScanDetailResponse
    comparison_summary: str
    safer_choice: str
    key_differences: List[Dict[str, Any]]


class ScreenshotExtractionResponse(BaseModel):
    status: Literal["SUCCESS", "EMPTY", "UNAVAILABLE", "ERROR"]
    extracted_text: str
    ocr_engine: str
    character_count: int
    error_code: Optional[str] = None
    reason: str = ""
    review_token: str
    filename: str


class ReviewedScreenshotRequest(BaseModel):
    content: str = Field(min_length=1, max_length=50000)
    review_token: str = Field(min_length=16, max_length=4000)
    target_identifier: Optional[str] = Field(default=None, max_length=255)
