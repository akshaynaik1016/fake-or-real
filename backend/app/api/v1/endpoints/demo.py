from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.schemas.all_schemas import ScanDetailResponse
from app.services.demo_seed import get_demo_cases
from app.api.v1.endpoints.analyze import _persist_and_format_scan

router = APIRouter(prefix="/demo", tags=["Hackathon Demo"])

@router.get("/cases")
def list_demo_cases():
    return get_demo_cases() if settings.DEMO_MODE else []

@router.post("/run/{case_id}", response_model=ScanDetailResponse)
async def run_demo_case(case_id: str, db: Session = Depends(get_db)):
    case = next((c for c in get_demo_cases() if c["id"] == case_id), None)
    if not settings.DEMO_MODE or case is None:
        raise HTTPException(404, "Demo case not found or demo mode disabled")
    return await _persist_and_format_scan(db, case["input_type"], case["content"],
        case["target_identifier"], synthetic=True)
