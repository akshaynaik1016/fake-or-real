from fastapi import APIRouter
from app.schemas.all_schemas import EmergencyTriageRequest, EmergencyGuidanceResponse
from app.services.emergency_service import get_emergency_guidance

router = APIRouter(prefix="/emergency", tags=["Emergency Triage"])

@router.post("/analyze", response_model=EmergencyGuidanceResponse)
def analyze_emergency_incident(req: EmergencyTriageRequest):
    guidance = get_emergency_guidance(req.incident_type)
    return EmergencyGuidanceResponse(**guidance)
