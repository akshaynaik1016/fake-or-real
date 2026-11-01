from collections import Counter
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.access import current_actor
from app.models.all_models import Scan, CommunityReport

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def get_dashboard_metrics(db: Session = Depends(get_db), actor=Depends(current_actor)):
    query = db.query(Scan)
    if actor and actor.role != "ADMIN":
        query = query.filter(Scan.user_id == actor.id)
    scans = query.order_by(Scan.created_at.desc()).all()
    reports = db.query(CommunityReport).all()
    counts = Counter(s.risk_level for s in scans)
    days = [datetime.now(timezone.utc).date() - timedelta(days=i) for i in reversed(range(7))]
    return {"stats": {"opportunities_checked": len(scans), "safe_count": counts["LOW RISK"],
        "needs_verification": counts["MODERATE RISK"], "high_risk": counts["HIGH RISK"],
        "critical_risk": counts["CRITICAL RISK"], "reports_submitted": len(reports)},
        "charts": {"risk_distribution": [{"name": name, "value": counts[key], "color": color}
            for name, key, color in [("Low Risk", "LOW RISK", "#10b981"), ("Needs Verification", "MODERATE RISK", "#f59e0b"),
                                      ("High Risk", "HIGH RISK", "#f43f5e"), ("Critical Risk", "CRITICAL RISK", "#ef4444")]],
            "category_distribution": [{"category": k, "count": v} for k, v in Counter(r.scam_category for r in reports).items()],
            "scans_over_time": [{"day": d.isoformat(), "scans": sum(s.created_at.date() == d for s in scans),
                "threats": sum(s.created_at.date() == d and s.risk_level in {"HIGH RISK", "CRITICAL RISK"} for s in scans)} for d in days]},
        "recent_scans": [{"id": s.id, "target_identifier": s.target_identifier, "input_type": s.input_type,
            "trust_score": s.trust_score, "risk_level": s.risk_level, "created_at": s.created_at.isoformat()} for s in scans[:5]]}
