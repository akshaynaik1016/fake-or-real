from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.config import settings
from app.security.redaction import redact_sensitive_credentials
from app.models.all_models import CommunityReport
from app.schemas.all_schemas import CommunityReportCreate, CommunityReportResponse, CommunityStats

router = APIRouter(prefix="/community", tags=["Community Reporting"])

# Default seeded community complaints
DEFAULT_COMMUNITY_FEED = [
    {
        "scam_category": "fake_internship",
        "organization_name": "Microsoft Impersonator",
        "target_domain": "microsoft-careers-india.xyz",
        "description": "Received WhatsApp message claiming I was selected for Microsoft AI internship. Asked to pay ₹999 registration fee via UPI.",
        "evidence_text": "Payment requested to microsoft.careers@okhdfcbank",
        "upvotes": 28
    },
    {
        "scam_category": "job_scam",
        "organization_name": "Fast Remote Jobs Pvt Ltd",
        "target_domain": "quick-internships-direct.top",
        "description": "Promised ₹4,000 daily for SMS sending. Asked for ₹1,499 refundable security deposit before sending task file.",
        "evidence_text": "Telegram contact requested UPI transfer",
        "upvotes": 19
    },
    {
        "scam_category": "fake_scholarship",
        "organization_name": "Global Tech Fund",
        "target_domain": "scholarship-portal-gov.online",
        "description": "Claimed $5000 Google scholarship, then asked for $250 processing and courier charge via gift card.",
        "evidence_text": "Urgency timer: 'Pay within 2 hours or award forfeited'",
        "upvotes": 14
    }
]

@router.get("/reports", response_model=List[CommunityReportResponse])
def get_community_reports(limit: int = 50, db: Session = Depends(get_db)):
    reports = db.query(CommunityReport).order_by(CommunityReport.created_at.desc()).limit(limit).all()
    if not reports and settings.DEMO_MODE:
        # Seed default feed items
        for item in DEFAULT_COMMUNITY_FEED:
            r = CommunityReport(
                scam_category=item["scam_category"],
                organization_name=item["organization_name"],
                target_domain=item["target_domain"],
                description="[Synthetic demo report] " + item["description"],
                evidence_text=item["evidence_text"],
                upvotes=item["upvotes"]
            )
            db.add(r)
        db.commit()
        reports = db.query(CommunityReport).all()
        
    return [CommunityReportResponse.model_validate(r) for r in reports]

@router.post("/reports", response_model=CommunityReportResponse)
def submit_community_report(req: CommunityReportCreate, db: Session = Depends(get_db)):
    new_report = CommunityReport(
        target_url=req.target_url,
        target_domain=req.target_domain,
        target_phone=req.target_phone,
        target_email=req.target_email,
        organization_name=req.organization_name,
        scam_category=req.scam_category,
        description=redact_sensitive_credentials(req.description),
        evidence_text=redact_sensitive_credentials(req.evidence_text or ""),
        status="APPROVED",
        upvotes=1
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return CommunityReportResponse.model_validate(new_report)

@router.get("/stats", response_model=CommunityStats)
def get_community_stats(db: Session = Depends(get_db)):
    reports = db.query(CommunityReport).all()
    total = len(reports) or 27
    
    breakdown = {
        "Payment Requests / Deposits": 18,
        "Fake Internship Offers": 6,
        "Credential / Aadhaar Harvesting": 3
    }
    top_domains = [
        {"domain": "microsoft-careers-india.xyz", "report_count": 14, "risk": "CRITICAL"},
        {"domain": "quick-internships-direct.top", "report_count": 8, "risk": "HIGH"},
        {"domain": "scholarship-portal-gov.online", "report_count": 5, "risk": "CRITICAL"}
    ]
    recent = db.query(CommunityReport).order_by(CommunityReport.created_at.desc()).limit(5).all()
    
    return CommunityStats(
        total_reports=total,
        scam_category_breakdown=breakdown,
        top_reported_domains=top_domains,
        recent_reports=[CommunityReportResponse.model_validate(r) for r in recent]
    )
