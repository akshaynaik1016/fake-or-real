from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.database import get_db
from app.models.all_models import Scan, VerificationResult, ScanEvidence
from app.schemas.all_schemas import TrustPassportResponse

router = APIRouter(prefix="/trust-passport", tags=["Trust Passport"])

@router.get("/{scan_id}", response_model=TrustPassportResponse)
async def get_trust_passport(scan_id: str, db: Session = Depends(get_db)):
    from app.services.investigation_store import scan_response
    detail = await scan_response(db, scan_id)
    scan = db.get(Scan, scan_id)
    from app.services.verification_service import verification_summary
    checks=detail['verification_results']
    counts=verification_summary(checks)
    passed_count=counts['verified']
    total_checks=len(checks)
    summary=counts['text']+". Completed checks do not verify offer authenticity."

    return TrustPassportResponse(
        scan_id=scan.id,
        opportunity_name=scan.target_identifier or "Evaluated Online Opportunity",
        organization=detail["investigation"].get("claimed_organization"),
        website=next((e["value"] for e in detail["investigation"]["entities"] if e["type"] == "domain"), None),
        trust_score=detail["trust_score"],
        risk_level=detail["risk_level"],
        analysis_confidence=detail["analysis_confidence"],
        verification_checks_passed=passed_count,
        total_verification_checks=total_checks,
        evidence_count=len(detail["evidence"]),
        qr_code_url=f"/trust-passport/{scan.id}",
        last_analyzed=scan.created_at,
        assessment=detail["assessment"],
        verification_summary=summary
    )
