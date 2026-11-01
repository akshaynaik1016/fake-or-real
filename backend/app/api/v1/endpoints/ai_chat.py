from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.all_schemas import AIChatRequest, AIChatResponse
from app.services.ai_investigator import answer_investigator_query
from app.services.investigation_store import scan_response

router = APIRouter(prefix="/ai", tags=["AI Investigator"])

@router.post("/investigate", response_model=AIChatResponse)
async def investigate_with_ai(req: AIChatRequest, db: Session = Depends(get_db)):
    detail = await scan_response(db, req.scan_id)
    state = detail["investigation"]
    detail["claimed_organization"] = state["claimed_organization"]
    detail["primary_domain"] = next((e["value"] for e in state["entities"] if e["type"] == "domain"), None)
    result = answer_investigator_query(req.question, detail)
    result["evidence_ids"] = [e["id"] for e in state["evidence"] if e["evidence"] in result["evidence_referenced"]]
    return AIChatResponse(**result)
