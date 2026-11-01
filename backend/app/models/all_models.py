from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="USER")  # USER, ANALYST, ADMIN
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    scans = relationship("Scan", back_populates="user")
    community_reports = relationship("CommunityReport", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), unique=True, index=True, nullable=False)
    official_domain = Column(String(255), nullable=True, index=True)
    official_website = Column(String(500), nullable=True)
    verified = Column(Boolean, default=False)
    country = Column(String(100), default="Global")
    registration_number = Column(String(100), nullable=True) # e.g. CIN for MCA
    official_careers_url = Column(String(500), nullable=True)
    known_aliases = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    domain_name = Column(String(255), unique=True, index=True, nullable=False)
    registrable_domain = Column(String(255), index=True, nullable=False)
    created_date = Column(DateTime, nullable=True)
    age_days = Column(Integer, nullable=True)
    registrar = Column(String(255), nullable=True)
    is_suspicious_tld = Column(Boolean, default=False)
    has_valid_ssl = Column(Boolean, default=False)
    dns_records = Column(JSON, default=dict)
    reputation_score = Column(Float, default=50.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class EmailAddress(Base):
    __tablename__ = "email_addresses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    domain = Column(String(255), index=True, nullable=False)
    is_free_provider = Column(Boolean, default=False)
    is_disposable = Column(Boolean, default=False)
    reputation = Column(String(50), default="neutral")


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    number = Column(String(50), unique=True, index=True, nullable=False)
    country_code = Column(String(10), nullable=True)
    is_voip = Column(Boolean, default=False)
    carrier = Column(String(100), nullable=True)
    report_count = Column(Integer, default=0)


class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    opportunity_type = Column(String(50), nullable=False) # internship, job, scholarship, etc.
    claimed_organization = Column(String(255), nullable=True)
    associated_url = Column(String(1000), nullable=True)
    description = Column(Text, nullable=True)
    salary_or_stipend = Column(String(100), nullable=True)
    fee_requested = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    input_type = Column(String(50), nullable=False) # url, text, screenshot, pdf, email, phone, org
    input_content = Column(Text, nullable=False)
    target_identifier = Column(String(500), nullable=True) # e.g. domain or title
    
    status = Column(String(50), default="COMPLETED") # QUEUED, ANALYZING, COMPLETED, FAILED
    trust_score = Column(Integer, nullable=False, default=50) # 0-100
    risk_level = Column(String(50), nullable=False, default="MODERATE RISK") # LOW, MODERATE, HIGH, CRITICAL
    analysis_confidence = Column(Integer, nullable=False, default=85) # 0-100
    
    summary = Column(Text, nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    user = relationship("User", back_populates="scans")
    evidence = relationship("ScanEvidence", back_populates="scan", cascade="all, delete-orphan")
    indicators = relationship("RiskIndicator", back_populates="scan", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="scan", cascade="all, delete-orphan")


class ScanEvidence(Base):
    __tablename__ = "scan_evidence"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, index=True)
    category = Column(String(100), nullable=False) # payment_request, domain_mismatch, etc.
    severity = Column(String(50), nullable=False) # low, moderate, high, critical, verified
    evidence = Column(Text, nullable=False)
    source = Column(String(100), nullable=False) # user_submission, dns, rdap, ocr, ssl, etc.
    confidence = Column(Float, default=1.0)
    explanation = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    scan = relationship("Scan", back_populates="evidence")


class RiskIndicator(Base):
    __tablename__ = "risk_indicators"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)
    is_positive = Column(Boolean, default=False) # positive signal vs risk flag
    
    scan = relationship("Scan", back_populates="indicators")


class VerificationResult(Base):
    __tablename__ = "verification_results"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, index=True)
    check_name = Column(String(100), nullable=False) # organization, domain, email, ssl, etc.
    status = Column(String(20), nullable=False) # passed, warning, failed
    details = Column(Text, nullable=True)
    
    scan = relationship("Scan", back_populates="verification_results")


class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    target = Column(String(500), index=True, nullable=False)
    provider = Column(String(100), nullable=False) # GoogleSafeBrowsing, VirusTotal, URLhaus, AbuseIPDB, DemoIntel
    is_flagged = Column(Boolean, default=False)
    threat_type = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    queried_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CommunityReport(Base):
    __tablename__ = "community_reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    target_url = Column(String(1000), nullable=True, index=True)
    target_domain = Column(String(255), nullable=True, index=True)
    target_phone = Column(String(50), nullable=True, index=True)
    target_email = Column(String(255), nullable=True, index=True)
    organization_name = Column(String(255), nullable=True)
    scam_category = Column(String(100), nullable=False) # fake_internship, job_scam, fee_fraud, etc.
    description = Column(Text, nullable=False)
    evidence_text = Column(Text, nullable=True)
    status = Column(String(50), default="APPROVED") # PENDING, APPROVED, REJECTED
    upvotes = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    user = relationship("User", back_populates="community_reports")


class UploadedDocument(Base):
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    extracted_text = Column(Text, nullable=True)
    metadata_json = Column(JSON, default=dict)
    auto_delete_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="audit_logs")


class SavedReport(Base):
    __tablename__ = "saved_reports"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), nullable=False, index=True)
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=True)
    report_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InvestigationState(Base):
    """Additive snapshot table; existing scans/evidence columns are unchanged."""
    __tablename__ = "investigation_states"
    scan_id = Column(String(36), ForeignKey("scans.id"), primary_key=True)
    revision = Column(Integer, nullable=False, default=1)
    payload = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class InvestigationExecution(Base):
    __tablename__ = "investigation_executions"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=False, index=True)
    action_id = Column(String(100), nullable=False)
    revision = Column(Integer, nullable=False)
    result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InvestigationCase(Base):
    __tablename__ = "investigation_cases"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(200), nullable=False)
    status = Column(String(30), nullable=False, default="NEEDS_EVIDENCE")
    revision = Column(Integer, nullable=False, default=0)
    assessment = Column(JSON, nullable=False, default=dict)
    research_calls = Column(Integer, nullable=False, default=0)
    research_results = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class InvestigationSource(Base):
    __tablename__ = "investigation_sources"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("investigation_cases.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    input_type = Column(String(30), nullable=False)
    submitted_content = Column(Text, nullable=False, default="")
    extracted_text = Column(Text, nullable=False, default="")
    filename = Column(String(255), nullable=True)
    processing_status = Column(String(30), nullable=False, default="PROCESSING")
    extraction_status = Column(String(30), nullable=False, default="NOT_PERFORMED")
    error_code = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    metadata_json = Column(JSON, nullable=False, default=dict)
    scan_id = Column(String(36), ForeignKey("scans.id"), nullable=True)
    analysis = Column(JSON, nullable=False, default=dict)
    removed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ExtractedClaim(Base):
    __tablename__ = "case_extracted_claims"
    id = Column(String(36), primary_key=True)
    source_id = Column(String(36), ForeignKey("investigation_sources.id"), nullable=False, index=True)
    claim_type = Column(String(60), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    normalized_value = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=False)
    location = Column(JSON, nullable=False)
    extraction_method = Column(String(60), nullable=False)
    verification_status = Column(String(60), nullable=False, default="CLAIMED")

class CrossSourceFinding(Base):
    __tablename__ = "cross_source_findings"
    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("investigation_cases.id"), nullable=False, index=True)
    kind = Column(String(70), nullable=False)
    classification = Column(String(60), nullable=False)
    severity = Column(String(30), nullable=False)
    description = Column(Text, nullable=False)
    citations = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False, default=True)

class CaseAssessmentRevision(Base):
    __tablename__ = "case_assessment_revisions"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("investigation_cases.id"), nullable=False, index=True)
    revision = Column(Integer, nullable=False)
    event = Column(String(80), nullable=False)
    snapshot = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (Index("uq_case_revision", "case_id", "revision", unique=True),)
