from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.all_schemas import ComparisonRequest, ComparisonResponse, ScanDetailResponse
from app.services.investigation_store import scan_response

router = APIRouter(prefix="/compare", tags=["Opportunity Comparison"])

@router.post("", response_model=ComparisonResponse)
async def compare_opportunities(req: ComparisonRequest, db: Session = Depends(get_db)):
    a = await scan_response(db, req.scan_id_a)
    b = await scan_response(db, req.scan_id_b)
    return ComparisonResponse(opportunity_a=ScanDetailResponse(**a), opportunity_b=ScanDetailResponse(**b),
        comparison_summary="Compare recorded evidence and coverage. Risk and independent verification are separate; missing evidence is unresolved.",
        safer_choice="Undetermined — compare cited concerns; neither offer is authenticated",
        key_differences=[{"dimension": key, "opportunity_a": a[key], "opportunity_b": b[key]}
                         for key in ("trust_score", "risk_level", "analysis_confidence")])
