from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.access import current_actor
from app.models.all_models import User
from app.core.config import settings
from app.core.database import get_db
from app.models.all_models import Scan, ScanEvidence, VerificationResult
from app.schemas.all_schemas import ScanResponse, ScanDetailResponse, EvidenceItem, VerificationCheckItem, ScanCreateRequest
from app.services.scan_service import execute_full_scan

router = APIRouter(prefix="/scans", tags=["Scans"])

@router.get("", response_model=List[ScanResponse])
def list_scans(limit: int = 50, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    query = db.query(Scan)
    if actor and actor.role != "ADMIN":
        query = query.filter(Scan.user_id == actor.id)
    scans = query.order_by(Scan.created_at.desc()).limit(max(1, min(limit, 100))).all()
    return [ScanResponse.model_validate(s) for s in scans]

@router.post("", response_model=ScanDetailResponse)
async def create_scan_endpoint(req: ScanCreateRequest, db: Session = Depends(get_db), actor: Optional[User] = Depends(current_actor)):
    from app.api.v1.endpoints.analyze import _persist_and_format_scan
    return await _persist_and_format_scan(
        db=db,
        input_type=req.input_type,
        content=req.content,
        target_identifier=req.target_identifier,
        user_id=actor.id if actor else None
    )

@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan_by_id(scan_id: str, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan record not found.")
        
    from app.services.investigation_store import scan_response
    return ScanDetailResponse(**(await scan_response(db, scan_id)))
