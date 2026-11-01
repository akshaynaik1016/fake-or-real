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
    from app.services.dashboard_investigations import summarize_investigations
    investigations=summarize_investigations(db,actor,details)
    counts = Counter(s['risk_level'] for s in details)
    synthetic_reports=[r for r in reports if (r.description or '').startswith('[Synthetic demo report]')]
    report_counts=Counter(r.scam_category for r in reports);demo_counts=Counter(r.scam_category for r in synthetic_reports)
    days = [datetime.now(timezone.utc).date() - timedelta(days=i) for i in reversed(range(7))]
    return {"investigation_stats":{**investigations["stats"],"reports_submitted":len(reports)},"investigation_risk_distribution":investigations["risk_distribution"],"risk_indicator_distribution":investigations["risk_indicator_distribution"],"investigation_basis":investigations["basis"],"investigation_case_count":investigations["case_count"],"standalone_scan_count":investigations["standalone_count"],"data_scope":{"scans":"Stored scans visible to this account, including case-source analyses and any demo scans; not unique authenticated opportunities.","reports":"Stored shared community report records; not confirmed incidents or scanner taxonomy counts.","synthetic_report_count":len(synthetic_reports),"submitted_report_count":len(reports)-len(synthetic_reports),"synthetic_scan_count":sum(bool(s.is_demo) for s in scans)},"stats": {"opportunities_checked": len(scans), "safe_count": 0,
        "needs_verification": counts["UNDETERMINED"], "high_risk": counts["ELEVATED CONCERN"],
        "critical_risk": 0, "reports_submitted": len(reports)},
        "charts": {"risk_distribution": [{"name": name, "value": counts[key], "color": color}
            for name, key, color in [("Undetermined", "UNDETERMINED", "#f59e0b"),("Elevated concern", "ELEVATED CONCERN", "#f43f5e")]],
            "category_distribution": [{"category": k, "count": v,"synthetic_count":demo_counts[k],"submitted_count":v-demo_counts[k]} for k, v in report_counts.items()],
            "scans_over_time": [{"day": d.isoformat(), "scans": sum(s.created_at.date() == d for s in scans),
                "threats": sum(s["created_at"].date()==d and s["risk_level"]=="ELEVATED CONCERN" for s in details)} for d in days]},
        "recent_scans": [{k:s[k] for k in ['id','target_identifier','input_type','trust_score','risk_level','assessment','created_at']} for s in details[:5]]}
