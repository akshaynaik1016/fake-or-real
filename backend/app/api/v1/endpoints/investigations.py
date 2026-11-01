from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.all_models import Scan
from app.services.investigation_store import load_state
from app.services.investigation_execution import execute_recommendation

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("/{scan_id}")
async def get_investigation(scan_id: str, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(404, "Scan not found")
    return await load_state(db, scan)


@router.get("/{scan_id}/{section}")
async def get_section(scan_id: str, section: str, db: Session = Depends(get_db)):
    if section not in {"evidence", "research", "graph", "fusion", "recommendations", "history"}:
        raise HTTPException(404, "Unknown investigation section")
    state = await get_investigation(scan_id, db)
    return state[section]


class ExecuteRequest(BaseModel):
    expected_revision: int = Field(ge=1)


@router.post("/{scan_id}/actions/{action_id}")
async def execute_action(scan_id: str, action_id: str, req: ExecuteRequest,
                         db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(404, "Scan not found")
    return await execute_recommendation(db, scan, action_id, req.expected_revision)
