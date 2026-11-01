from collections import Counter
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.access import current_actor
from app.models.all_models import Scan, CommunityReport

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
async def get_dashboard_metrics(db: Session = Depends(get_db), actor=Depends(current_actor)):
    query = db.query(Scan)
    if actor and actor.role != "ADMIN":
        query = query.filter(Scan.user_id == actor.id)
    scans = query.order_by(Scan.created_at.desc()).all()
    reports = db.query(CommunityReport).all()
    from app.services.investigation_store import scan_response
    details=[await scan_response(db,s.id) for s in scans]
    counts = Counter(s['risk_level'] for s in details)
    days = [datetime.now(timezone.utc).date() - timedelta(days=i) for i in reversed(range(7))]
    return {"stats": {"opportunities_checked": len(scans), "safe_count": 0,
        "needs_verification": counts["UNDETERMINED"], "high_risk": counts["ELEVATED CONCERN"],
        "critical_risk": 0, "reports_submitted": len(reports)},
        "charts": {"risk_distribution": [{"name": name, "value": counts[key], "color": color}
            for name, key, color in [("Undetermined", "UNDETERMINED", "#f59e0b"),("Elevated concern", "ELEVATED CONCERN", "#f43f5e")]],
            "category_distribution": [{"category": k, "count": v} for k, v in Counter(r.scam_category for r in reports).items()],
            "scans_over_time": [{"day": d.isoformat(), "scans": sum(s.created_at.date() == d for s in scans),
                "threats": sum(s["created_at"].date()==d and s["risk_level"]=="ELEVATED CONCERN" for s in details)} for d in days]},
        "recent_scans": [{k:s[k] for k in ['id','target_identifier','input_type','trust_score','risk_level','assessment','created_at']} for s in details[:5]]}
