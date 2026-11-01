from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.core.config import settings
from app.models.all_models import User, Scan, CommunityReport, AuditLog

router = APIRouter(prefix="/admin", tags=["Admin Portal"])

@router.get("/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    scans_count = db.query(Scan).count()
    critical_scans = db.query(Scan).filter(Scan.risk_level == "CRITICAL RISK").count()
    reports_count = db.query(CommunityReport).count()
    
    return {
        "total_users": users_count,
        "total_scans": scans_count,
        "critical_scans": critical_scans,
        "community_reports": reports_count,
        "api_health": "Serving requests; uptime not measured",
        "worker_health": "Inline execution; no queue configured",
        "active_scoring_weights": settings.DEFAULT_WEIGHTS,
        "threat_intel_status": {
            "GoogleSafeBrowsing": "Configured" if settings.SAFE_BROWSING_API_KEY else "UNAVAILABLE",
            "VirusTotal": "UNAVAILABLE (adapter not implemented)",
            "URLhaus": "UNAVAILABLE (adapter not implemented)",
            "DemoIntelligence": "Synthetic cases only"
        }
    }

@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs

@router.post("/weights")
def update_scoring_weights(new_weights: Dict[str, float]):
    import math
    if set(new_weights) != set(settings.DEFAULT_WEIGHTS) or any(not math.isfinite(v) or v < 0 for v in new_weights.values()):
        raise HTTPException(400, "Provide all known weights with finite, nonnegative values")
    total = sum(new_weights.values())
    if abs(total - 1.0) > 0.05:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sum of weights must equal 1.0 (current sum: {total:.2f})"
        )
    settings.DEFAULT_WEIGHTS.update(new_weights)
    return {"status": "SUCCESS", "updated_weights": settings.DEFAULT_WEIGHTS}
