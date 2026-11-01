import uuid
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all_models import SavedReport
from app.schemas.all_schemas import SavedReportResponse
from app.services.investigation_store import scan_response
from app.services.report_generator import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/{scan_id}/save", response_model=SavedReportResponse)
async def save_report(scan_id: str, db: Session = Depends(get_db)):
    from fastapi.encoders import jsonable_encoder
    detail = await scan_response(db, scan_id)
    report = SavedReport(scan_id=scan_id, share_token=uuid.uuid4().hex,
        title=f"Trust & Safety Audit — {detail['target_identifier'] or 'Report'}",
        report_data=jsonable_encoder({"scan_id": scan_id, **detail}), is_public=False)
    db.add(report)
    db.commit()
    db.refresh(report)
    return SavedReportResponse.model_validate(report, from_attributes=True)

@router.get("/{report_id}", response_model=SavedReportResponse)
async def get_saved_report(report_id: str, db: Session = Depends(get_db)):
    report = db.query(SavedReport).filter((SavedReport.id == report_id) |
        (SavedReport.share_token == report_id) | (SavedReport.scan_id == report_id)).first()
    if report:
        return SavedReportResponse.model_validate(report, from_attributes=True)
    return await save_report(report_id, db)

@router.get("/{scan_id}/pdf")
async def download_report_pdf(scan_id: str, db: Session = Depends(get_db)):
    detail = await scan_response(db, scan_id)
    return Response(content=generate_pdf_report(detail), media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=FakeOrReal-Audit-{scan_id[:8]}.pdf"})
